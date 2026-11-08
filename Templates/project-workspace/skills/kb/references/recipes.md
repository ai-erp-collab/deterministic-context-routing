# Promoting a platform technique to a recipe

A recipe is a reusable platform technique ("how to do X with the
platform"), never one module's business rule. A business rule stays in
its owner module and is reached through that module's contract.

Promotion waits until the technique has stopped changing.

1. Register a candidate when a session stabilized such a technique:
   `kb recipe candidate add <file> --symbol <Symbol> --module <Module>`
   (add `--params <types>` to pick one overload).
2. At each session close in that module, record the current state:
   `kb recipe candidate tick --module <Module>`.
3. `kb recipe candidates` lists candidates whose code stayed unchanged
   for the configured number of closes (default 3). Ask the user whether
   to promote one. Promotion needs the user's yes.
4. On yes:

   ```
   python tools/kb/kb.py recipe promote <file> --symbol <Symbol> --domain <domain> --title "<title>" --owner <Module>
   ```

   The tool writes `knowledge-base/shared/recipes/<domain>/<slug>.md`
   with the donor hash and adds a row to
   `knowledge-base/shared/patterns/INDEX.md`. It refuses to overwrite an
   existing recipe. Edit the page: replace module constants in the
   snippet with parameters and add adaptation notes.
5. `kb recipe drift` reports recipes whose donor code changed or
   disappeared. Review the recipe against the new code and update it.

To inspect a symbol without registering it, use
`kb recipe extract <file> --symbol <Symbol>`.
