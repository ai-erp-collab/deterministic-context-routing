# Turning a table export into table pages

1. Ingest the export first (`references/ingest.md`).
2. Run `kb table <export> --module <Module>`. Add `--shared` to write
   the pages under `knowledge-base/shared/tables/`, and
   `--encoding <code page>` for a text export that is neither UTF-8 nor
   UTF-16.
3. Exit 0: the layout was recognized. The tool writes or updates one
   page per table (structure only, `confidence: schema-confirmed`)
   and reports what changed. An existing page for the same table is
   updated, never duplicated; curated descriptions stay.
4. Exit 3: no known layout matched. The output lists the best header
   candidate rows with numbered columns. Decide which row is the header
   and which column holds each role (`field` is required; others:
   `description`, `type`, `length`, `precision`, `nullable`,
   `key_position`, `sample`, `sub_table`, `notes`). Then register the
   layout:

   ```
   python tools/kb/kb.py table learn <export> --name <layout> --header-row 2 --map field=1,type=3,description=4
   ```

   The tool parses the export with that mapping, prints the first parsed
   fields, and saves the profile only if parsing works. Show that sample
   to the user once for each new layout before generating pages, then
   run `kb table <export> --module <Module>` again. Later exports with
   the same layout are detected without asking.

After generation, curate the business meaning: purpose, keys, relations
to other tables, and confidence labels on everything inferred.
