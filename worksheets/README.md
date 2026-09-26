# MathWorksheets4Kids → lesson tagging (work in progress)

This branch holds the work to tag every MathWorksheets4Kids sheet in the school Drive
("MathWorksheets4Kids Sheets" folder) to the small steps of the curriculum site.
The live site (`main`) is not affected.

## Status

### Stage 1: describe every worksheet (DONE)
`catalogue.json` / `catalogue.csv` hold 3,748 worksheet sets (K–G6) with what each one
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

### Stage 2: verify file IDs and answer-key pairings (NOT DONE)
Helpers reported a few mis-paired answer keys and one ID that pointed to the wrong file.
Before matching:
1. Finish the exact Drive listing of all 177 folders (`tools/LIST_PROMPT.md`; `listing/`
   holds the part-done listing).
2. Check every `id` / `answer_key_id` against it.
3. Re-check any sheet whose description came from a mismatched answer key.

Warning: never run several large Drive searches at the same time. Their results can
overwrite each other.

### Stage 3: match worksheets to lessons (NOT STARTED)
`lessons/lessons_N.json` holds the 934 small steps in 47 chunks. Two sets of instructions:
- `tools/MATCH_PROMPT.md` proposes core and prerequisite worksheets for each lesson.
- `tools/VERIFY_PROMPT.md` independently re-checks every match.

### Stage 4: review spreadsheet, then Stage 5: paperclip-panel UI (NOT STARTED)

## Tools
- `tools/render.py` renders a downloaded Drive PDF to page images.
- `tools/merge.py` shows how the catalogue was merged.
