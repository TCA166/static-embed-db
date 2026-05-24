# Static embedding search

Comprehensive solution for providing context-aware static file search.

## Usage

1. Pick a specific embedding model

```sh
python3 save_model.py --model <your_model_name>
```

2. Generate the embeddings for your static files

```sh
python3 generate.py ./files/*.tex
```

3. Serve the embeddings

```sh
npm run dev
```
