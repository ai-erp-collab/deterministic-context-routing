# Looking up before writing a page

Two pages for one subject drift apart. Before creating a page, look up
what already exists.

1. Run `kb resolve "<name>"`. It matches page names, titles, `aliases:`
   lines, concept terms, and glossary cards; it ignores case and
   separators and maps Cyrillic and Latin spellings onto each other.
   Narrow with `--kind <kind>` (for example `table`, `class`, `term`)
   or `--domain <domain>`; add `--fulltext` to search page text when
   names fail.
2. A confident hit: update that page instead of writing a new one. Add
   the name you searched for to its `aliases:` line if it was missing.
3. No hit: write the new page from `templates/wiki/`, and give it an
   `aliases:` line with the other names people use.

Placement:
- A fact about one module goes under `knowledge-base/modules/<module>/`.
- A fact several modules rely on goes under `knowledge-base/shared/`;
  module pages link to it instead of repeating it.
- A table described in both places is a duplicate: keep one page and
  link to it from the other location.

When the duplicate check reports two pages and the user says both are
intended, record that with `kb config accept-duplicate <path> <path>`.
