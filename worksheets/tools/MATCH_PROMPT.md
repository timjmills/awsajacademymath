# Task: match MathWorksheets4Kids worksheets to curriculum lessons (small steps)

A school's maths website lists every lesson ("small step") of its curriculum. Teachers will see, for each lesson, the worksheets you choose. A wrong match wastes a teacher's time and undermines trust, so **precision matters more than quantity** — but within that, be exhaustive: list every worksheet that genuinely fits.

## Inputs
- Your lessons: `SCRATCH/ws/match/lessons_CHUNK.json` — a list of units; each unit has `grade` (site grade: PK, K, G1–G5), `unit` name, and `steps` (each with `step`, `title`, `ccss` codes, `note`). Grades follow US Common Core: site G3 = US Grade 3 (content from White Rose Maths Year 4). Read the whole unit's step list so you understand the teaching sequence (what comes before and after each step).
- The worksheet catalogue: `SCRATCH/ws/catalogue.tsv` (tab-separated; ~3,500 rows). Columns: id, grade (K, G1–G6 = the folder's grade), topic, num_title, kind, ccss, status, does (what the sheet ACTUALLY asks — verified by reading/looking at it), notes. Search it with python/grep via Bash; do NOT load it all into your context. The `does` and `notes` fields are the truth — titles can be misleading, and folder grades are sometimes wrong (notes flag this).

## What to produce, per lesson
1. **core** — worksheets that directly practise THIS lesson's skill at an appropriate level: same operation/concept, suitable number sizes and representation, and doable by a student who has just had this lesson (not needing skills taught later). Include all that genuinely fit. Order them easiest → hardest.
2. **prereq** — worksheets for the most important prerequisite skills this lesson builds on (usually from lower grades or earlier in the unit). Choose the best 2–6, each tied to a named prerequisite skill. Only include if clearly useful for a student who is not ready for the lesson.
For every pick give a short `why` (≤15 words) naming the specific match (e.g. "3-digit subtraction with regrouping, column method").

## Rules
- Only use worksheets whose `status` is True/true/visual/answer key. Never use status False (unverified).
- Never use: non-maths sheets (word searches, reading, crafts), blank templates, or pure decoration. Reference charts only if the lesson is directly about that content, and mark why "reference chart".
- Money lessons: US currency only unless the lesson is explicitly not US money. Flag customary vs metric where the lesson specifies units.
- Level check: reject sheets whose numbers or methods are clearly beyond or below the lesson (e.g. a Grade 2 lesson on 2-digit addition should not get 4-digit sheets; a lesson on "add ones" should not get regrouping sheets).
- A lesson may legitimately have zero core matches — then say so. Do not force matches. Lessons flagged `committee` have no White Rose materials; still match worksheets to them.
- If two worksheets are duplicates (notes say so), pick one.
- Search broadly: check the lesson's grade and the grades either side (catalogue grade K–G6), by topic, ccss, and keywords in `does`. Kindergarten sheets serve PK lessons.

## Output
Write one JSON object per lesson (one per line) to `SCRATCH/ws/match/out_CHUNK.jsonl`:
`{"grade":"G3","unitNum":2,"unit":"...","step":4,"title":"...","core":[{"id":"...","why":"..."}],"prereq":[{"id":"...","skill":"...","why":"..."}],"note":"anything the reviewer should know"}`
Append as you go. Temporary files go only under `SCRATCH/ws/tmp_mCHUNK/`. When done, check every lesson in your input has exactly one line. Reply briefly: lessons done, total core picks, total prereq picks, lessons with zero core matches.

## RESUMING
If `SCRATCH/ws/match/out_CHUNK.jsonl` already exists, skip lessons already in it and append only the missing ones.
