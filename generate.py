import json
import re
from pathlib import Path

import torch
from optimum.onnxruntime import ORTModelForFeatureExtraction
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_for_filename
from pygments.token import Text
from pygments.util import ClassNotFound
from sympy import SympifyError
from sympy.parsing.latex import LaTeXParsingError, parse_latex
from tqdm import tqdm
from transformers import AutoTokenizer

CLEAN = re.compile(r"\\[a-zA-Z]+\{.*?\}|\\[a-zA-Z]+")


def chunk_text(text: str, n: int):
    chunk = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        words = line.split()
        take = n - len(words)
        chunk.extend(words[:take])
        if len(chunk) >= n:
            yield " ".join(chunk), i
            chunk = []

    if chunk:
        yield " ".join(chunk), len(lines) - 1


def get_plaintext_tokens(text: str, lexer: Lexer):
    math_content: str | None = None
    latex_mode = lexer.name == "TeX"

    for type, token in lexer.get_tokens(text):
        if (token == "$$" or token == "$") and latex_mode:
            if math_content is not None:
                math_content = math_content.strip()
                try:
                    parsed = parse_latex(math_content)
                except (LaTeXParsingError, TypeError, SympifyError):
                    parsed = math_content
                math_content = None
                yield parsed
            else:
                math_content = ""
            continue

        if math_content is not None:
            math_content += token
            continue

        if type is Text:
            yield token


def extract_plain_text(text: str, lexer: Lexer) -> str:
    tokens = get_plaintext_tokens(text, lexer)
    plain_text = "".join(str(token) for token in tokens)
    return plain_text


def get_embedding(
    text: str, model: ORTModelForFeatureExtraction, tokenizer: AutoTokenizer
):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
    return embedding


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate embeddings for files")
    parser.add_argument("files", nargs="+", help="List of files to process")
    parser.add_argument(
        "--n", type=int, default=20, help="Chunk width (words per chunk)"
    )
    parser.add_argument(
        "--model", default="./static/model", help="Sentence-transformers model name"
    )
    parser.add_argument(
        "--outfile", default="./static/embeddings.json", help="Output JSON file"
    )
    parser.add_argument("--raw", action="store_true", help="Output raw text chunks")
    args = parser.parse_args()

    model = ORTModelForFeatureExtraction.from_pretrained(args.model)
    tokenizer = AutoTokenizer.from_pretrained(args.model)

    result = []
    for fname in tqdm(args.files, desc="Processing files"):
        fname = Path(fname)

        with open(fname, "r", encoding="utf-8") as f:
            contents = f.read()

        if not args.raw:
            try:
                lexer = get_lexer_for_filename(fname.name)
                contents = extract_plain_text(contents, lexer)
            except ClassNotFound as e:
                print(f"Warning: {e}")
                contents = CLEAN.sub("", contents)

        chunks = tuple(chunk_text(contents, args.n))
        if not chunks:
            continue

        for (chunk, line), embedding in zip(
            chunks, (get_embedding(chunk, model, tokenizer) for chunk, _ in chunks)
        ):
            result.append(
                {
                    "file": fname.name,
                    "chunk": chunk,
                    "embedding": embedding.tolist(),
                    "line": line,
                }
            )

    # Save to JSON
    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Saved {len(result)} embeddings to {args.outfile}")


if __name__ == "__main__":
    main()
