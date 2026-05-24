#!/bin/bash

set -e

while getopts "m:" opt; do
  case $opt in
    m)
      MODEL="$OPTARG"
      ;;
  esac
done
shift $((OPTIND -1))

pip install -r requirements.txt
mkdir -p public

if [ -n "$MODEL" ]; then
  python3 save_model.py -model "$MODEL"
else
  python3 save_model.py
fi

python3 generate.py "$@"
npm install
npm run build
