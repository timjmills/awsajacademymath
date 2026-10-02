# Task: verify RELATED-skill worksheet picks that nobody has seen yet

Input: `SCRATCH/ws/rel/vin_PART.json` — items {grade, unit, step, title (the lesson, with NO direct worksheet), id (Drive file id), relation, why (how it was said to relate), catalogue_title, answer_key_id}. Each pick was suggested from catalogue text only. Teachers will see these as "Related skills"; they must really be related and usable.

For EACH item actually look at the worksheet, one Drive call at a time (never parallel):
1. `read_file_content` on id. If text is garbled/empty, try `read_file_content` on answer_key_id (answer keys usually extract cleanly and show the questions and answers).
2. If still unclear: `download_file_content` on id; if it is saved to a file, render with `python3 SCRATCH/ws/render.py <saved json> <id> SCRATCH/ws/rel/img_vPART` and Read the PNG (render.py refuses mismatched downloads). If it only comes back inline you cannot render it.
Never delete files you did not create; exact paths only, no globs; delete only your own img folder.

Verdict per item:
- "keep": you saw it (say what) and it genuinely relates to the lesson as the `why` says (a teacher could use it, perhaps with 'use only the first N items').
- "drop": different skill, far too hard/easy, not practice (reference chart, cut-and-glue only), non-US money, or content differs from the why.
- "unconfirmed": you could not see the content at all (then it will be dropped).
Never say "keep" for something you did not see.

Write `SCRATCH/ws/rel/vout_PART.jsonl`, one line per item: {"id","grade","unit","step","verdict","saw":"<short>","fix_why":"<optional corrected one-sentence why, e.g. which items to use>"}. Reply with counts per verdict.
