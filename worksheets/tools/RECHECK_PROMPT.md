# Task: re-check worksheets whose description may belong to another file

Earlier, some PDF downloads got swapped (two downloads at the same moment overwrote each other), so these worksheets may have been described from the wrong file's pages, or wrongly called "duplicates". Re-check each one from its own file.

List: `SCRATCH/ws/recheck/todo_PART.json` (catalogue entries plus `recheck_reason`).
Load tools once: ToolSearch `select:mcp__Google_Drive__download_file_content,mcp__Google_Drive__read_file_content`.

RULES: make Drive calls ONE AT A TIME (never two in one message). Process each result before the next call.

For each entry:
1. `download_file_content` with the entry's id. If saved to a file, run `python3 SCRATCH/ws/render.py <path> <id> SCRATCH/ws/tmp_r_PART/img`. render.py prints the file's real title and REFUSES if the download is for a different file — if it says MISMATCH, download again (one call) and retry.
2. Look at the page images (Read) — at least page 1, plus 2–3 if they differ. If the download came back inline instead of saved, use `read_file_content` on the WORKSHEET id first; if that text is garbled, use the answer key only if its title matches this worksheet (check with read_file_content output title).
3. Decide what the sheet really asks. Compare with the current `does`. If this sheet was called a duplicate of another file, say whether that's really true (look at both if needed, one download at a time).
4. Append the full corrected entry (all original fields; update does/skills/ccss/kind/sheets/us_specific/notes; set text_ok "visual" or "text"; add "recheck":"confirmed" if the old description was right or "recheck":"corrected" if you changed it) as one JSON line to `SCRATCH/ws/recheck/fixed_PART.jsonl`. If you truly cannot check it, set text_ok false and say why.
5. Delete files you created (exact paths only).
Skip ids already in fixed_PART.jsonl (resume). Reply with counts: confirmed / corrected / could not check, and list the corrected titles.
