# Source for the domain sequence

These scripts produced `domain_sequence.json` and the workbook. The site pipeline stays the source of truth; this folder documents exactly how the order was derived, so you can check it or rerun it on newer data.

Run from this folder, in order (Python 3, `openpyxl`):

```
python3 final_map.py     # sequence per grade  -> final_map.json
python3 coverage.py      # CCSS coverage       -> ccss_cov.json
python3 examcheck.py     # booklet question check -> examcheck_rows.json
python3 xlsx_map.py      # workbook            -> out/WRM_Domain_Sequence_K-5.xlsx
python3 export.py        # build data          -> out/domain_sequence.json, out/domain_sequence.csv
python3 assesscheck.py   # optional: prints the exam-check summary
```

| Script | Role |
|---|---|
| `core.py` | Loads WRM_to_CCSS_Mapping_v3 steps and the pacing-guide text; recovers WRM teaching order by matching each lesson title to its first appearance in the guide (anchored on the CCSS code that follows it). |
| `plan.py` | Assigns each step a domain (grade-level code first; power-standard domain wins on ties; Grade 6-only steps go to enrichment); prerequisite edges between domains (`edges`). |
| `mapplan.py` | Chooses the domain order: every permutation that respects the edges, scored by (1) all grade-level standards taught by W32, (2) last exam by W32, (3) S1/S2 power-standard balance, (4) closeness to WRM order. Places the MAP row and the enrichment block. |
| `final_map.py` | Builds the final sequence: copies in the 7 gap-closing steps (`COPIES`), adds teaching notes (`MANUAL`), labels enrichment by grade, spreads items over 39 weeks. |
| `crossgrade.py` | Full CCSS list per grade (from the mapping's coverage tables) and cross-grade gap analysis. |
| `assesscheck.py`, `examcheck.py` | Check every booklet question's standard against the sequence. |
| `inputs/` | Mapping workbook text, pacing-guide text and per-week TSVs, and the tagged booklet questions (`assess_items_<grade>.tsv`). |

Known limits: prerequisite edges are domain-level judgements from CCSS, not WRM's small-step dependency notes; 7% of lesson titles did not match the guide text and were placed beside their unit neighbours.

## Changes made in the site repo (October 2026)

- **Calendar:** items are spread over the live site's 39 weeks (W01 = 6 Sep) in proportion to teaching days (`core.assign_weeks`, `inputs/site_weeks.json`). Semester 1 ends at W14.
- **Current White Rose scheme only:** `inputs/renames.json` maps 7 old-scheme titles to their current names; other old-scheme (2020-21) steps that are not on the White Rose Drive or the live site are dropped (`core.current`). Every current White Rose step is kept.
- **BUILD lessons** whose names contain digits (for example "Count on to 120") are no longer skipped.
- **Copied-in steps:** "What is volume?" is not in the current Year 5 scheme, so Grade 5 copies "Cubic centimetres" only.
- **Domain tests:** `inputs/domain_tests.json` holds the Drive ids of the Awsaj domain booklets used by the exam rows.
- `inputs/assess_items_<grade>.tsv` (the tagged booklet questions) are not in this public repo; add them locally to run `assesscheck.py` / `examcheck.py`.

To rebuild the preview after `final_map.py` and `export.py`:

```
python3 build_preview.py   # writes ../../preview/index.html from ../../index.html
python3 accept.py          # brief section 7 checks
```

`build_preview.py` finds the repo root two folders up (or set `AWSAJ_REPO`). `inputs/live_pills.json` is the support panel per live week, captured from the live page.

## Preview and printed documents

`./make_preview.sh` rebuilds `preview/index.html`, then the K-G5 Weekly Pacing Guides and Teaching & Pacing Handbooks (`gen_docs.py` writes HTML, `render_docs.js` prints PDFs with Playwright) and the K-5 pacing workbook (`gen_xlsx.py`) into `preview/docs/`. The workbook carries no exam question content.
