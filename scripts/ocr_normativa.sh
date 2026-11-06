#!/bin/sh
# Preparación opcional del original escaneado; no ejecuta comandos al ingerir.
# Requiere poppler-utils, tesseract-ocr y tesseract-ocr-spa.
set -eu
input="$1"
output="$2"
mkdir -p "$output"
pdftoppm -r 200 -png "$input" "$output/page" >/dev/null 2>&1
for page in "$output"/page-*.png; do
    tesseract "$page" "${page%.png}" -l spa --psm 3 >/dev/null 2>&1
done
