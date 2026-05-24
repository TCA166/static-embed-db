# Static embedding search

Comprehensive solution for providing context-aware static file search.
By default, built for static deployment of LaTeX files with open sources, but
can be adapted for any static file type.

## Usage

1. Pick a specific embedding model

```sh
python3 save_model.py --model <your_model_name>
```

2. Generate the embeddings for your static files

```sh
python3 generate.py ../notes/*/*.tex --strip_paths 3
```

Here the `--strip_paths 3` option strips the first 2 path components from the
file name. The saved file links will be automatically adjusted to point to the
PDF files, however, manually may be changed using the `--path_suffix .pdf`
option.

3. Serve the embeddings

```sh
npm run dev
npm run build
```

**Alternatively** you can just run `./build.sh` to build the embeddings and
the frontend into a single output directory `dist/`.

```sh
./build.sh ../notes/*/*.tex --strip_paths 3
```

## GitHub Actions

This repository includes a GitHub Actions workflow component, which can be used
to automate the embedding and deployment process.

```yaml
name: Test Static Embed DB Action

jobs:
  build-embed-db:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: TCA166/static-embed-db@main # or @v1 after tagging
        with:
          glob: '../*/*.tex'
          strip_paths: 1
```
