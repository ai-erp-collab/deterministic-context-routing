# Source Artifacts

Evidence copied into the workspace. `kb ingest` copies each file to `<kind>/raw/<module>/` and records its
origin and hash in `registry.json`; this file is generated from that registry by `tools/kb/kb.py`.

- Do not rewrite raw files unless the project has an explicit normalization rule.
- A file is processed once a curated page names it in its `source:` line; `kb fix --safe` then sets the
  status. Files never move between folders, so links to them stay valid.

| Artifact | Status | Module | Curated pages | Notes |
| --- | --- | --- | --- | --- |
