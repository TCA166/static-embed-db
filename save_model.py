import os
import shutil

from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer


def main():
    import argparse

    parser = argparse.ArgumentParser("Save a model to disk in ONNX format")
    parser.add_argument(
        "--model", type=str, default="sentence-transformers/all-MiniLM-L6-v2"
    )
    parser.add_argument("--model_dump", type=str, default="./public/model")
    args = parser.parse_args()

    onnx_model = ORTModelForFeatureExtraction.from_pretrained(args.model, export=True)
    onnx_model.save_pretrained(args.model_dump)

    # Save tokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    tokenizer.save_pretrained(args.model_dump)

    # Move ONNX file to the expected subdirectory and name
    onnx_subdir = os.path.join(args.model_dump, "onnx")
    os.makedirs(onnx_subdir, exist_ok=True)
    shutil.copyfile(
        os.path.join(args.model_dump, "model.onnx"),
        os.path.join(onnx_subdir, "model_quantized.onnx"),
    )


if __name__ == "__main__":
    main()
