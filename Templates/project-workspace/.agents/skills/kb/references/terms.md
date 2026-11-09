# Resolving an unknown term

1. Run `kb resolve "<term>"` (add `--kind term` to see glossary cards
   only). Matching covers abbreviations and transliterations recorded
   as aliases.
2. A confident hit: read that page and continue.
3. No confident hit: find the meaning in the evidence (table exports,
   documents, code comments). If the evidence does not settle it, ask
   the user. Do not guess a meaning into the knowledge base.
4. Record the answer where the next session will find it:
   - a term used by one module: its concept page, under
     `## Core Entities` or `## Terminology`;
   - a term several modules use: a card in
     `knowledge-base/shared/glossary/<slug>.md` from
     `templates/wiki/glossary-term-page.md`, with `term:`, `aliases:`
     (abbreviations, transliterations, other spellings), `domain:`,
     `owner:`, and a confidence label.
5. The write hook reindexes the page, so the next lookup finds it.
