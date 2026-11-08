# Tables As Contracts


## Reader Outcome

After this section, the reader can:

- Explain why ERP tables are business contracts, not only storage.
- Create a table page that records business meaning, important fields, relations, codes, and uncertainty.
- Keep raw table exports separate from curated table knowledge.
- Check for an existing page before writing one, so each table has exactly one page.
- Register a new export layout once, so later exports of that layout are parsed by the tool instead of by hand.
- Use confidence labels when a table fact is schema-confirmed but runtime-unverified.
- Route future agents from module language to table evidence without forcing them to read raw exports.

## Core Explanation

In proprietary ERP systems, tables are rarely passive storage. A table can define document identity, workflow state, access scope, hierarchy, formula setup, user grouping, status transitions, reporting dimensions, or configuration behavior. A developer can change code correctly and still break the feature if the table contract is misunderstood.

This is why the methodology treats tables as contracts.

A table contract is not a raw schema dump. The raw schema says which fields exist. The contract explains what future work may rely on: what the table is for, which business terms it materializes, which fields are important, how rows relate to other tables, which codes or statuses carry business meaning, and which facts remain uncertain.

The contract should connect three layers:

- business language: terms from the module concept, user requests, documents, statuses, roles, and workflows;
- structural evidence: exported schemas, recognized artifacts, keys, fields, types, nullability, indexes, and relations;
- runtime behavior: how the table is read or written by libraries, UI actions, workflows, formulas, reports, permissions, or setup screens when that behavior is known.

The difference matters. A field can be schema-confirmed because it appears in an export. Its business meaning may still be inferred. Its runtime behavior may still be runtime-unverified. The table page must keep those states separate.

A table page has three required sections: `Keys`, `Fields`, and `Relations`. Relations are the part most often skipped and the part a change most often breaks, so a page marked `kind: table` without them is reported by the integrity check from section 03 as incomplete. A relation that is not known yet is written down as an open question, not left out.

Each table has exactly one page. When the same table is described twice, for example once on a shared page and once in a module, the two descriptions drift apart and an agent may read the wrong one. The rule is to look before writing: `kb resolve <table name>` finds an existing page by name or alias, and the integrity check reports pages that share a name. Choosing which description survives is a judgment call, so the check never merges pages itself.

### Table Exports And Layout Profiles

Table exports arrive as spreadsheets or text files, and each export tool has its own column layout. Parsing such a file by hand in every session is slow and error-prone: one session reads the type column as the length column, the next session repeats the work. The integrity layer turns this into a one-time step. The command `kb table <export> --module <Module>` recognizes a known layout by its header words and writes or updates one page per table. The structure it extracts carries `confidence: schema-confirmed`; purpose, relations, and business meaning stay for curation. If a page for the same table already exists, the command updates its field list and reports the difference instead of creating a second page.

When no known layout matches, the command stops with exit code 3 and prints the most likely header rows with numbered columns. The agent proposes which row is the header and which column holds each role (only the field name is required; type, length, description, key position, and similar roles are optional) and registers the layout with `kb table learn <export> --name <layout> --header-row <row> --map field=<n>,type=<n>,...`. The tool parses the export with that mapping and saves the layout profile only if parsing works. The agent shows the parsed sample to the user once per new layout. From then on, exports with that layout are recognized without asking. Layout profiles are project data in `.kb/profiles/`; none ship with the template, because header words are project-specific.

The table page is also a context-routing device. It should be the small entry point that lets an agent understand the table without reading every export or source usage. It should summarize the contract and link to deeper evidence: artifact index entries, source examples, class contracts, usage flows, and open questions.

## Reproducible Procedure

1. Start from a concrete knowledge need.
   - Name the module, task, or business term that requires table knowledge.
   - Avoid normalizing tables only because they exist.

2. Locate permitted evidence.
   - Check existing table pages and module wiki first.
   - Use recognized table exports when available.
   - Register newly found XML, CSV, TXT, or similar exports as evidence with `kb ingest`, which copies them into the artifact area and records them in the registry.
   - Use source examples, user documentation, or runtime observations only when they are permitted and relevant.

3. Preserve the raw artifact.
   - Do not edit raw exports in place.
   - Record where the artifact came from and what it is believed to represent.
   - Keep the raw artifact as evidence, not as the table contract itself.

4. Create or refresh the table contract page.
   - Look for an existing page first with `kb resolve <table name>`; refresh it instead of writing a second one.
   - For a structured export, run `kb table <export> --module <Module>`. On exit code 3, register the layout with `kb table learn` and show the parsed sample to the user before generating pages.
   - State the table purpose in business language.
   - List aliases, natural names, abbreviations, and module terms.
   - Record source artifacts and confidence labels.
   - Fill the required sections `Keys`, `Fields`, and `Relations`; write an unknown relation as an open question.
   - Identify important fields, codes, and statuses.
   - Link to classes, usage flows, documents, reports, or UI actions that use the table.

5. Separate confirmed facts from inferred meaning.
   - Mark fields and types from recognized schemas as schema-confirmed, not as plain confirmed, until business meaning and runtime behavior are also verified.
   - Mark business meaning as confirmed, inferred, runtime-unverified, or blocked-by-access according to the evidence. Use the page's `status: partial` for incompleteness; never use `partial` as a claim-level label.
   - State what runtime check would confirm behavior that cannot be verified statically, and mark it runtime-confirmed once observed.

6. Keep the page small enough to route context.
   - Summarize important fields instead of copying the entire export.
   - Link to the artifact index for full source evidence.
   - Use related-notes links for contracts, flows, and examples.

7. Complete the artifact lifecycle.
   - Review the generated or refreshed page for extraction errors.
   - Name the evidence copy in the page's `source:` line; the integrity check then marks the registry row `processed`. Files are not moved.

## Required Artifacts

- Registered evidence copy of each export, with its registry row (`raw` until a curated page names it, then `processed`).
- Table contract page with `Keys`, `Fields`, and `Relations` sections.
- Layout profile in `.kb/profiles/` for each export layout the project uses.
- Links from module concept, usage flows, or class contracts when the table is important to them.
- Confidence labels for important table claims.
- Open questions for unresolved meanings, relations, codes, or runtime behavior.

## Example

A budgeting task refers to a "parent budget unit." The term sounds like a business concept, but implementation depends on table structure.

The table-contract workflow should not start by loading every budget export. It should route context:

- read the budgeting module concept to understand the business term;
- check existing table pages for hierarchy or budget-unit tables;
- inspect recognized exports only for the relevant tables;
- identify fields that represent parent-child relations, active periods, codes, or grouping;
- link source examples or access-rule contracts that read those fields;
- mark whether the relation is schema-confirmed, inferred from source usage, or runtime-unverified for real data.

The resulting table page should let a future agent answer: "Which table stores this relationship, which fields matter, how confident are we, and where is the deeper evidence?"

## Failure Modes

- Treating a schema dump as documentation: fields exist, but their business meaning remains invisible.
- Treating a field name as proof of meaning: a plausible relation becomes a false contract.
- Mixing raw and curated evidence: future readers cannot tell what was exported and what was interpreted.
- Marking schema-confirmed facts as runtime-confirmed behavior.
- Copying large exports into wiki pages: the table page stops being a useful context-routing entry point.
- Omitting codes and statuses: the most important business behavior remains hidden.
- Omitting used-by links: agents cannot connect data structure to code behavior.
- Marking an artifact processed before the wiki is refreshed and reviewed.
- Writing a second page for a table that already has one: the two descriptions drift and agents read the wrong one.
- Parsing the same export layout by hand in every session: the work repeats and the column roles are read differently each time.
- Treating generated structure as curated knowledge: the page lists fields but says nothing about purpose or relations.

## Assumptions And Runtime Limits

- A table contract can start partial when the uncertainty is explicit.
- Exported schemas can confirm structure, but not every business meaning or runtime behavior.
- Real data, configuration, permissions, and workflow state may be needed to confirm behavior.
- A table page should point to raw evidence, not replace it.

## Related Notes

- `03-knowledge-system.md`: defines source evidence, curated memory, and context routing.
- `06-knowledge-acquisition.md`: defines permitted evidence and confidence labels.
- `08-libraries-and-class-contracts.md`: explains behavior contracts that often read or write tables.
- `09-usage-flows-and-patterns.md`: downstream section for scenarios that connect several tables and classes.
- `Methodology/Wiki/insights.md`: records tables-as-contracts as a core insight.
