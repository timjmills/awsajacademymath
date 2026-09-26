# Task: list every file in a set of Google Drive folders (exact, complete)

Folders: `SCRATCH/ws/listing/folders_PART.json` (list of {id, grade, topic}).
1. Load tools: ToolSearch `select:mcp__Google_Drive__search_files`.
2. For each folder call `search_files` with query `parentId = '<id>'`, pageSize 1000, excludeContentSnippets true. Follow `nextPageToken` until none. Results that are too large are saved to a file (the error gives the path) — parse with python via Bash. If a folder contains sub-folders, list them too.
3. Write, for each file, one JSON line `{"id":..,"title":..,"parentId":..,"folder_id":<the batch folder id>,"mimeType":..}` to `SCRATCH/ws/listing/files_PART.jsonl` (append per folder; de-duplicate by id). Copy ids and titles programmatically from the tool output — never retype them.
4. Temporary files only under `SCRATCH/ws/tmp_lPART/`. Reply with: folders listed, total files.
If `files_PART.jsonl` already exists, skip folders whose folder_id already appears in it.
