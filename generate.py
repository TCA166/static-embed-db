import json
import re

import torch
from optimum.onnxruntime import ORTModelForFeatureExtraction
from tqdm import tqdm
from transformers import AutoTokenizer

CLEAN = re.compile(r"\\[a-zA-Z]+\{.*?\}|\\[a-zA-Z]+")


def chunk_text(text: str, n: int) -> list[str]:
    cleaned = CLEAN.sub("", text)
    words = cleaned.split()
    chunks = [
        " ".join(words[i : i + n])
        for i in range(0, len(words), n)
        if len(words[i : i + n]) >= 0.5 * n
    ]
    return chunks


def get_embedding(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
    return embedding


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate embeddings for .tex files")
    parser.add_argument("files", nargs="+", help="List of .tex files to process")
    parser.add_argument(
        "--n", type=int, default=100, help="Chunk width (words per chunk)"
    )
    parser.add_argument(
        "--model", default="./public/model", help="Sentence-transformers model name"
    )
    parser.add_argument(
        "--outfile", default="./public/embeddings.json", help="Output JSON file"
    )
    args = parser.parse_args()

    model = ORTModelForFeatureExtraction.from_pretrained(args.model)
    tokenizer = AutoTokenizer.from_pretrained(args.model)

    result = []
    for fname in tqdm(args.files, desc="Processing .tex files"):
        with open(fname, "r", encoding="utf-8") as f:
            tex = f.read()
        chunks = chunk_text(tex, args.n)
        if not chunks:
            continue
        embeddings = [get_embedding(chunk, model, tokenizer) for chunk in chunks]
        for chunk, embedding in zip(chunks, embeddings):
            result.append(
                {"file": fname, "chunk": chunk, "embedding": embedding.tolist()}
            )

    # Save to JSON
    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Saved {len(result)} embeddings to {args.outfile}")


if __name__ == "__main__":
    main()
