# Task: exact listing of Google Drive folders (with integrity checks)

Folders to list: `SCRATCH/ws/list2/folders_PART.json` (list of {id, grade, topic}).

Load tools once: ToolSearch `select:mcp__Google_Drive__search_files`.

RULES (important — earlier runs corrupted data by breaking these):
- Make Drive calls ONE AT A TIME. Never put two Drive tool calls in the same message.
- When a result is too large it is saved to a file whose path is in the error. Read it with python immediately (before the next Drive call).
- Copy ids/titles programmatically (python/json), never by retyping.

For each folder:
1. Call `search_files` with query `parentId = '<folder id>'`, pageSize 1000, excludeContentSnippets true. Follow `nextPageToken` until there is none (one call at a time).
2. INTEGRITY CHECK: every returned file must have `parentId` equal to the folder id you asked for. If any don't, the result got mixed up — discard it and repeat that call.
3. If there are sub-folders (mimeType folder), list them too the same way.
4. Write `SCRATCH/ws/list2/f_<folder id>.json` = {"folder_id":..,"grade":..,"topic":..,"files":[{"id","title","parentId","mimeType"}...]} de-duplicated by id. Write this file only after the folder is complete.
Skip folders whose f_<id>.json already exists (resume). Temporary files only under `SCRATCH/ws/tmp_l2_PART/`.
Reply with: folders done, total files, any folder you could not complete.
