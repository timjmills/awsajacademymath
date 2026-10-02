# Task: independent spot-audit of worksheet <-> lesson matches

You audit randomly sampled picks from a list that maps MathWorksheets4Kids worksheets to curriculum lessons. Teachers will rely on it; the school does not want mistakes. Be an independent, honest judge.

Input: `SCRATCH/ws/audit3/sample_PART.json` — 16 items {grade (site grade, US Common Core; site G3 = US Grade 3), unit, step, title (the lesson), id (Drive file id), why (why it was matched), catalogue_title, sheet_grade}.

For EACH item you must actually OPEN the worksheet and look at it, one Drive call at a time (never two in parallel):
- Try `read_file_content` on the id first. If the text is garbled or empty, use `download_file_content`; results come back inline or saved to a file. If saved to a JSON file, render with `python3 SCRATCH/ws/render.py <saved json> <id> SCRATCH/ws/audit3/img_PART` and view page 1 PNG with Read. render.py refuses a mismatched download. If you can only get garbled text and no image, try the answer key (the id with title "... Answer Key" is not available; just say could not open).
- NEVER delete files you did not create; use exact paths, no globs. Delete only your own img folder at the end.

Judge each item with a verdict:
- "good": the sheet practises the lesson's skill at a level a teacher could use (easier/harder grade is fine if the why says so).
- "weak": usable but loose fit (partial skill, extra content beyond lesson).
- "wrong": different skill, far too hard/easy, not a practice sheet (reference chart, cut-and-glue only), wrong currency (non-US money), or content differs from the why.
- "unopened": you could not see the content.
Never claim "good" for something you did not see. Say what you actually saw in a short "saw" field.

Write `SCRATCH/ws/audit3/result_PART.jsonl`: one line per item: {"id":..,"verdict":..,"saw":"<short>","issue":"<short or empty>"}. Reply with counts per verdict and the ids judged wrong.
