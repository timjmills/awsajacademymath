# Task: independently check worksheet ↔ lesson matches

Another agent matched MathWorksheets4Kids worksheets to curriculum lessons. You are the independent checker. Teachers will rely on this list and the school has said it does not want mistakes. Be strict: when in doubt, reject.

## Inputs
- Lessons: `SCRATCH/ws/match/lessons_CHUNK.json` (units with ordered steps: title, ccss, note). Site grades follow US Common Core (site G3 = US Grade 3).
- Proposed matches: `SCRATCH/ws/match/out_CHUNK.jsonl` (one line per lesson: core and prereq picks with a `why`).
- Catalogue: `SCRATCH/ws/catalogue.tsv` (tab-separated: id, grade, topic, num_title, kind, ccss, status, does, notes). `does`/`notes` describe what each sheet ACTUALLY asks. Look up each proposed id there with python/grep — don't load the whole file into context.

## Automated check findings
If `SCRATCH/ws/match/problems_CHUNK.txt` exists, it lists problems found by an automated check on the matcher's output (non-practice sheets, prerequisites above the lesson's grade, wrong grade distance, etc.). Resolve EVERY item: remove the pick, or keep it and say why in its `why`. Then do the normal review below.

## For every proposed pick
Decide KEEP or REJECT:
- core: KEEP only if the sheet practises this lesson's specific skill, at a suitable level (number sizes, method, representation), and a student could do it right after this lesson. REJECT if it's a different skill, too hard/too easy, needs later lessons, non-US money for a US money lesson, non-maths, a blank template, unverified (status False), or a duplicate of another kept pick.
- prereq: KEEP only if it clearly practises a genuine prerequisite skill of this lesson and is easier/earlier than the lesson.
Also, for each lesson, do your own quick search of the catalogue for clearly-fitting core worksheets the matcher MISSED, and add them (mark `"added":true`). Only add ones you are sure about.

## Balance: do not over-reject, and do not skip the search
- Being from an EARLIER grade is NOT a reason to reject on its own. A sheet that practises exactly this lesson's skill at an easier level is fine as `core` — keep it and add "(easier, grade K)" style wording to its `why`. Reject for level only when the numbers/method are clearly beyond or too far from the lesson.
- A lesson with no worksheets is a gap. Before you reject the LAST core pick of a lesson, think about whether a close alternative exists; and for EVERY lesson with fewer than 3 core picks you MUST search the catalogue yourself for fitting sheets (python/grep on topic, ccss, skills, `does`) and add any that genuinely fit (`"added":true`).
- Do NOT reject a sheet merely because you could not open it: if it is small and the download came back inline, use `read_file_content` on the worksheet or its answer key. Reject as "could not open" only after both fail.
- Add `"searched":true` to every lesson line where you did the search above.

## Open every worksheet you keep (required)
About 3% of catalogue descriptions have a wrong detail, so before you KEEP any core or prereq pick (including ones you add), open that worksheet and confirm it really fits:
- Load tools once: ToolSearch `select:mcp__Google_Drive__download_file_content,mcp__Google_Drive__read_file_content`.
- Make Drive calls ONE AT A TIME (never two in one message).
- `download_file_content` with the id. If it was saved to a file, run `python3 SCRATCH/ws/render.py <path> <id> SCRATCH/ws/tmp_vCHUNK/img` and look at page 1 (and 2 if useful). render.py refuses if the download is for a different file — then download again.
- If the download came back inline, use `read_file_content` on the worksheet (check the returned title matches); if that text is garbled, use `read_file_content` on its answer key (find the answer key id in `SCRATCH/ws/stage2/catalogue.json`, field `answer_key_id`).
- If you cannot open it at all, REJECT it with reason "could not open".
- If the sheet differs from its catalogue description in a way that matters, say so in `why` and judge on what you SAW.
- The same worksheet often appears for several lessons in your chunk — open it once and reuse what you saw. Delete files you create (exact paths).

## Output
Write one JSON object per lesson (one per line) to `SCRATCH/ws/match/verified_CHUNK.jsonl`:
`{"grade":..,"unitNum":..,"step":..,"title":..,"core":[{"id":..,"why":..,"added":false,"opened":true}],"prereq":[{"id":..,"skill":..,"why":..}],"rejected":[{"id":..,"was":"core|prereq","reason":".."}],"note":".."}`
Keep the matcher's `why` for kept picks (improve it if inaccurate). Temporary files only under `SCRATCH/ws/tmp_vCHUNK/`. When done, check every lesson has exactly one line. Reply briefly with counts: kept, rejected, added.

## RESUMING
If `SCRATCH/ws/match/verified_CHUNK.jsonl` exists, skip lessons already in it and append only the missing ones.


## Honesty rule for the `opened` field
`"opened": true` means YOU personally opened that worksheet (or its answer key) in this run and it matched. If you relied on the catalogue description instead, set `"opened": false`. Never set it true otherwise. You do not have to open every pick: you MUST open every pick whose catalogue `status` is not `visual`, every pick marked above/below grade, every pick you restore or add, and any pick whose catalogue notes mention a doubt. For picks with status `visual` and no doubts, the catalogue description (made by looking at the pages) is acceptable evidence — but open as many as you reasonably can.
