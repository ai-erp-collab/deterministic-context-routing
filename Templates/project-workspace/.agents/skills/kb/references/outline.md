# Reading a large source file

A file larger than about 50 KB costs more context than it returns when
read whole. Read its outline first, then only the span you need.

1. Run `kb outline <file>`. The output starts with `tier: A|B` (the
   parser used) and the size before and after; then the skeleton:
   types, members, and signatures with line numbers, bodies skipped.
2. Pick the symbols the task needs and read only those line ranges of
   the file.
3. To keep the outline for later, write it to a file with
   `kb outline <file> --out <path>`.

If the outline says the extension has no family, the file's language is
unknown to the tool. Choose the closest family and register it, testing
it on this file:

```
python tools/kb/kb.py config family .xyz c-like --sample <file>
```

Families: `c-like` (brace languages), `python`, `keyword-block`
(begin/end languages; also pass `--start <regex>` and `--end <regex>`
for the block start and end lines), `sql`, `json`, `xml`, `markup`,
`plain`. The tool refuses the mapping if the sample outline is empty.
