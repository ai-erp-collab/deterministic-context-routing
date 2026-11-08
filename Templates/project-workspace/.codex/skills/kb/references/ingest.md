# Taking in evidence

Evidence is copied, never moved. The copy under `source-artifacts/` is
the stable one that pages link to; the original stays where it was.

1. Run `kb ingest <path...> --module <Module>` with the files or
   folders that arrived. Add `--kind <kind>` (`tables`, `docs`, `specs`,
   `code`) when the extension does not say it.
2. The tool copies each file into `source-artifacts/<kind>/raw/<module>/`,
   records the origin path and a hash in `source-artifacts/registry.json`,
   and regenerates `source-artifacts/INDEX.md`. Read the small `INDEX.md`;
   never edit either file by hand.
3. Ingesting a file again from the same origin refreshes its copy; the
   freshness check reports when an origin changed since intake.

Processed means a curated page names the copy in its `source:` line.
When you write that page, the hook marks the artifact processed. Files
never move between folders: `raw` or `processed` is a registry status.

Files under a module's `evidence:` folders (from `modules.md`) are
tracked too. A tracked file without a registry row is a blocking issue;
`kb fix --safe` adds the missing row as `raw`. To exclude files on
purpose, list them in `.kb/track.ignore` (gitignore syntax).
