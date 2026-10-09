#!/bin/sh
# Rebuild the preview page, then its printable PDFs and the workbook.
set -e
REPO=${AWSAJ_REPO:-/home/user/awsajacademymath}
python3 build_preview.py > /dev/null
python3 gen_docs.py inputs/adapt.json
mkdir -p "$REPO/preview/docs"
node render_docs.js out/docs "$REPO/preview/docs"
python3 gen_xlsx.py
cp out/docs/Awsaj-Domain-Sequence-K-5-2026-27.xlsx "$REPO/preview/docs/"
