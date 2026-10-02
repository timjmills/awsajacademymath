# Task: find RELATED-SKILL worksheets for lessons that have no direct worksheet

Input: `SCRATCH/ws/rel/in_PART.json` — lessons (site grade PK/K/G1..G5 = US Common Core grade; unit, step, title, note) for which NO MathWorksheets4Kids worksheet practises the exact skill. `previously_rejected` lists sheets earlier reviewers rejected (with reasons) — some may be usable as RELATED sheets.

Goal: for each lesson, find up to 3 worksheets a teacher could use for a closely RELATED skill, so the teacher is never left empty-handed. Acceptable relations (say which in `relation`):
- "earlier step": the skill just before it in the same unit (e.g. for "Subitise 4 and 5" a sheet counting objects to 5).
- "same skill, wider range": practises the same skill but includes numbers/items beyond the lesson (note: "use only the first items") — only if the beyond part is a small part of the sheet.
- "adjacent skill": the next/closest skill in the same topic.
- "easier version" of the skill (a lower grade sheet; for PK lessons grade K sheets are fine here if simple).
Do NOT pick a different topic, a pure colouring/craft sheet, a reference chart, non-US money, or a sheet far too hard.

Catalogue: `SCRATCH/ws/stage2/catalogue.tsv` (columns: id, grade, topic, num_title, kind, ccss, status, does, notes) — search it with grep/python for topic words; use only sheets whose status is text/visual/answer key (not False). Pick sheets by reading `does`.

For EACH sheet you pick you MUST open it and look (one Drive call at a time, never in parallel): `read_file_content` on the id; if garbled/empty use `download_file_content` then render page 1 with `python3 SCRATCH/ws/render.py <saved json> <id> SCRATCH/ws/rel/img_PART` and Read the PNG. render.py refuses mismatched downloads. Never delete files you did not create; exact paths only, no globs; delete only your own img folder at the end. If you cannot see the content, you may still list a sheet only if the catalogue `does` text is clear, with `opened:false`.

Output `SCRATCH/ws/rel/out_PART.jsonl`: one line per input lesson, copying grade, unit, step, title EXACTLY (grade a string like "PK"): {"grade","unit","step","title","related":[{"id":<full Drive id from catalogue>,"relation":"earlier step|same skill wider range|adjacent skill|easier version","why":"<one sentence incl. any 'use first N items'>","opened":true|false}],"note":"<short, e.g. 'no related sheet exists'>"}. An empty related list is fine when truly nothing fits — do not force it. Reply with: lessons done, lessons with ≥1 related, lessons with none.
