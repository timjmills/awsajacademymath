# Task: find worksheets whose description may belong to a different file

Earlier, some PDF downloads may have been swapped (two downloads at the same moment overwrote each other), so a few worksheets may have been described from the WRONG file's pages. Your job is to spot them by comparing each worksheet's file TITLE with its DESCRIPTION.

Input: `SCRATCH/ws/audit/rows_PART.json` — a list of {id, title, topic, checked, does, notes}. Process it in chunks of ~60 with python so you read everything (print each chunk, judge it, move on). Do not skip any rows.

For each row decide:
- "ok" — the description fits the title/topic (same skill; minor wording differences, different themes, or a title that is a bit vague are fine).
- "mismatch" — the description is about a clearly different skill/topic than the title (e.g. title "Adding Fractions Draw Hops" but description "decimal number line construction"; title in the Money folder but description about telling time). Also flag rows whose notes already say the content doesn't match the title, or mention a possible file/id mix-up.
Be careful and conservative: MathWorksheets4Kids titles are usually literal, so a real topic mismatch is suspicious. But do NOT flag differences in level, number range, sheet count, or format.

Write ONLY the flagged rows, one JSON line each, to `SCRATCH/ws/audit/flags_PART.jsonl`: {"id":..,"title":..,"does":..,"reason":"<short>"}. When done, reply with: rows checked, rows flagged. (Write an empty file if none are flagged.)
