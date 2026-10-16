#!/bin/sh
# Rebuild the whole thing: sequence -> coverage -> export -> live index.html -> PDFs and workbook.
set -e
REPO=${AWSAJ_REPO:-/home/user/awsajacademymath}
python3 final_map.py > /dev/null
python3 coverage.py > /dev/null
python3 examcheck.py
python3 export.py > /dev/null
python3 accept.py | grep -E "contiguous|exams"
python3 build_preview.py > /dev/null
python3 gen_docs.py inputs/adapt.json
mkdir -p "$REPO/preview/docs"
node render_docs.js out/docs "$REPO/preview/docs"
python3 gen_xlsx.py
cp out/docs/Awsaj-Domain-Sequence-K-5-2026-27.xlsx "$REPO/preview/docs/"
