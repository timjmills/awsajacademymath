# MathWorksheets4Kids → lesson tagging (work in progress)

This branch holds the work to tag every MathWorksheets4Kids sheet in the school Drive
("MathWorksheets4Kids Sheets" folder) to the small steps of the curriculum site.
The live site (`main`) is not affected.

## Status

### Stage 1: describe every worksheet (DONE)
`catalogue.json` / `catalogue.csv` hold 3,749 worksheet sets (K–G6) with what each one
actually asks. The descriptions come from the sheet's content, never from its file name:
- 2,392 checked by looking at rendered page images
- 1,012 checked from the extracted text
- 273 checked from the answer key, because the worksheet itself was unreadable
- 70 **unverified**: garbled fonts and a download that could not be rendered.
  Exclude these from tagging, or check them by hand.

Every row links to the worksheet and its answer key in Drive. The `notes` column flags:
- misleading file names
- non-US money
- sheets filed in the wrong grade
- non-maths "holiday" sheets
- duplicates

### Stage 2: verify IDs, pairings and descriptions (DONE)
- **Exact listing:** all 177 Drive folders, 7,336 files, relisted one folder at a time. Every result was checked to come from the folder that was asked for (`listing/`).
- **IDs:** all 3,748 catalogue IDs exist with the right titles.
  - 1 worksheet that stage 1 missed has now been catalogued, giving 3,749 in total.
- **Answer keys** (`stage2/validation_report.json`):
  - 76 were linked to the wrong worksheet; now fixed.
  - 181 existing keys had not been linked; now linked.
  - 4 links pointed at other worksheets; removed.
  - 162 sheets have no answer key in Drive.
- **Download mix-ups:** in stage 1, parallel downloads sometimes overwrote each other, so a few sheets were described from another sheet's pages.
  - A title-versus-description audit and a list of "duplicate" notes gave 141 suspects.
  - Each suspect was re-checked from its own file, with an ID check (`tools/render.py` now refuses a mismatched download).
  - 36 were corrected; the rest were confirmed.
- **Random sample:** 90 visually-checked, unflagged entries were re-checked.
  - No swapped files were found.
  - About 3% had a materially wrong detail, such as describing what students do too broadly.
  - Stage 3's checker should re-open any worksheet it is unsure about.
- **Unverified:** 50 remain. The fonts are unreadable and the PDF could not be rendered. Exclude these from tagging, or check them by hand.

### Stage 3: match worksheets to lessons (NOT STARTED)
`lessons/lessons_N.json` holds the 934 small steps in 47 chunks. Two sets of instructions:
- `tools/MATCH_PROMPT.md` proposes core and prerequisite worksheets for each lesson.
- `tools/VERIFY_PROMPT.md` independently re-checks every match.

### Stage 4: review spreadsheet, then Stage 5: paperclip-panel UI (NOT STARTED)

## Tools
- `tools/render.py` renders a downloaded Drive PDF to page images.
- `tools/merge.py` shows how the catalogue was merged.

## Stage 3 (matching) — done
All 934 lessons matched (3,072 core + 1,374 prerequisite picks; 174 lessons have no suitable catalogue sheet and are listed in the Gaps sheet).
Pipeline per chunk: matcher → independent checker (opens sheets, rejects bad fits, searches for misses) → recovery pass (restores wrongly rejected sheets, fills gaps) → automated checks (`tools/check_match.py`).
A random audit of 96 core picks (re-opened by 6 independent agents) found 75 good, 17 weak fit, 2 wrong (removed), 2 unopenable.
Review file for the committee: `Worksheet_Matches_Review.xlsx`. Final data: `stage3/stage3_final.json`.
