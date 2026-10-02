# Task: recover over-rejected worksheet matches and fill gaps

A first checker reviewed worksheet matches for curriculum lessons. Some checkers rejected too much (e.g. rejecting sheets only because they came from an earlier grade, or without opening them) and skipped searching for sheets the matcher missed. Your job is a SECOND, balanced pass over one chunk.

Inputs (SCRATCH = scratchpad dir): lessons `SCRATCH/ws/match/lessons_CHUNK.json`; matcher output `SCRATCH/ws/match/out_CHUNK.jsonl`; first checker output `SCRATCH/ws/match/verified_CHUNK.jsonl` (has `core`, `prereq`, `rejected`); catalogue `SCRATCH/ws/catalogue.tsv` (columns: id, grade, topic, num_title, kind, ccss, status, does, notes — search with python/grep, never load it all); full catalogue with answer-key ids `SCRATCH/ws/stage2/catalogue.json`.

For EVERY lesson:
1. Re-examine each item in `rejected`. Restore it if it genuinely fits the lesson: same skill, a level a student could do right after the lesson (an easier earlier-grade sheet that practises the exact skill is fine and should be restored with "(easier, grade X)" in its `why`). Keep it rejected if: different skill, clearly beyond the lesson, non-US money for US-money lessons, not maths, a blank template, status unverified, or a duplicate of a kept sheet. Rejections for "not opened" are NOT valid reasons — judge from the catalogue `does` text, and if unsure, open it (below).
2. For every lesson with fewer than 3 core picks, search the catalogue for sheets that fit and add them.
3. Every sheet you restore or add must be opened and confirmed (below). Sheets already kept by the first checker with `opened:true` need no re-opening.
4. Never use status False/unverified sheets.

How to open a sheet (Drive tools: ToolSearch `select:mcp__Google_Drive__download_file_content,mcp__Google_Drive__read_file_content`): make Drive calls ONE AT A TIME. `download_file_content` with the id; if saved to a file run `python3 SCRATCH/ws/render.py <path> <id> SCRATCH/ws/tmp_rCHUNK/img` and look at page 1 (render.py refuses a mismatched download — download again). If it came back inline, `read_file_content` on the worksheet (check the returned title); if garbled, `read_file_content` on its answer key (`answer_key_id` in stage2/catalogue.json). Delete files you create (exact paths).

Output: write the FINAL list for each lesson to `SCRATCH/ws/match/final_CHUNK.jsonl`, one JSON line per lesson with the same keys as the verified file (`grade`, `unitNum`, `unit`, `step`, `title`, `core`, `prereq`, `rejected`, `note`), copying the five identifying fields exactly from the input. Each core/prereq item: {"id","why","opened":true,...}. Include `"recovered":true` on restored items and `"added":true` on new ones. Also add `"gap":true` to a lesson that still has zero core picks after your search. Check at the end that every lesson in the lessons file has exactly one line. Reply with counts: restored, added, still rejected, lessons with zero core.


## Honesty rule for the `opened` field
`"opened": true` means YOU personally opened that worksheet (or its answer key) in this run and it matched. If you relied on the catalogue description instead, set `"opened": false`. Never set it true otherwise. You do not have to open every pick: you MUST open every pick whose catalogue `status` is not `visual`, every pick marked above/below grade, every pick you restore or add, and any pick whose catalogue notes mention a doubt. For picks with status `visual` and no doubts, the catalogue description (made by looking at the pages) is acceptable evidence — but open as many as you reasonably can.
