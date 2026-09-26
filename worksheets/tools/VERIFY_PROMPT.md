# Task: independently check worksheet ↔ lesson matches

Another agent matched MathWorksheets4Kids worksheets to curriculum lessons. You are the independent checker. Teachers will rely on this list and the school has said it does not want mistakes. Be strict: when in doubt, reject.

## Inputs
- Lessons: `SCRATCH/ws/match/lessons_CHUNK.json` (units with ordered steps: title, ccss, note). Site grades follow US Common Core (site G3 = US Grade 3).
- Proposed matches: `SCRATCH/ws/match/out_CHUNK.jsonl` (one line per lesson: core and prereq picks with a `why`).
- Catalogue: `SCRATCH/ws/catalogue.tsv` (tab-separated: id, grade, topic, num_title, kind, ccss, status, does, notes). `does`/`notes` describe what each sheet ACTUALLY asks. Look up each proposed id there with python/grep — don't load the whole file into context.

## For every proposed pick
Decide KEEP or REJECT:
- core: KEEP only if the sheet practises this lesson's specific skill, at a suitable level (number sizes, method, representation), and a student could do it right after this lesson. REJECT if it's a different skill, too hard/too easy, needs later lessons, non-US money for a US money lesson, non-maths, a blank template, unverified (status False), or a duplicate of another kept pick.
- prereq: KEEP only if it clearly practises a genuine prerequisite skill of this lesson and is easier/earlier than the lesson.
Also, for each lesson, do your own quick search of the catalogue for clearly-fitting core worksheets the matcher MISSED, and add them (mark `"added":true`). Only add ones you are sure about.

## Output
Write one JSON object per lesson (one per line) to `SCRATCH/ws/match/verified_CHUNK.jsonl`:
`{"grade":..,"unitNum":..,"step":..,"title":..,"core":[{"id":..,"why":..,"added":false}],"prereq":[{"id":..,"skill":..,"why":..}],"rejected":[{"id":..,"was":"core|prereq","reason":".."}],"note":".."}`
Keep the matcher's `why` for kept picks (improve it if inaccurate). Temporary files only under `SCRATCH/ws/tmp_vCHUNK/`. When done, check every lesson has exactly one line. Reply briefly with counts: kept, rejected, added.

## RESUMING
If `SCRATCH/ws/match/verified_CHUNK.jsonl` exists, skip lessons already in it and append only the missing ones.
