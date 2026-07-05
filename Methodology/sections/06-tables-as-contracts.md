# Tables As Contracts


## Reader Outcome

After this section, the reader can:

- Explain why ERP tables are business contracts, not only storage.
- Create a table page that records business meaning, important fields, relations, codes, and uncertainty.
- Keep raw table exports separate from curated table knowledge.
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

The table page is also a context-routing device. It should be the small entry point that lets an agent understand the table without reading every export or source usage. It should summarize the contract and link to deeper evidence: artifact index entries, source examples, class contracts, usage flows, and open questions.

## Reproducible Procedure

1. Start from a concrete knowledge need.
   - Name the module, task, or business term that requires table knowledge.
   - Avoid normalizing tables only because they exist.

2. Locate permitted evidence.
   - Check existing table pages and module wiki first.
   - Use recognized table exports when available.
   - Put newly found XML, CSV, TXT, or similar exports in the raw artifact area.
   - Use source examples, user documentation, or runtime observations only when they are permitted and relevant.

3. Preserve the raw artifact.
   - Do not edit raw exports in place.
   - Record where the artifact came from and what it is believed to represent.
   - Keep the raw artifact as evidence, not as the table contract itself.

4. Create or refresh the table contract page.
   - State the table purpose in business language.
   - List aliases, natural names, abbreviations, and module terms.
   - Record source artifacts and confidence labels.
   - Identify key fields, important fields, codes, statuses, and relations.
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
   - Move recognized artifacts to the processed area only after related wiki pages are created or refreshed.
   - Update the artifact index.

## Required Artifacts

- Raw source artifact when a new export is introduced.
- Processed source artifact after recognition and review.
- Artifact index entry.
- Table contract page.
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
- Moving raw artifacts to processed before the wiki is refreshed and reviewed.

## Assumptions And Runtime Limits

- A table contract can start partial when the uncertainty is explicit.
- Exported schemas can confirm structure, but not every business meaning or runtime behavior.
- Real data, configuration, permissions, and workflow state may be needed to confirm behavior.
- A table page should point to raw evidence, not replace it.

## Related Notes

- `02-knowledge-system.md`: defines source evidence, curated memory, and context routing.
- `05-knowledge-acquisition.md`: defines permitted evidence and confidence labels.
- `07-libraries-and-class-contracts.md`: explains behavior contracts that often read or write tables.
- `08-usage-flows-and-patterns.md`: downstream section for scenarios that connect several tables and classes.
- `Methodology/Wiki/insights.md`: records tables-as-contracts as a core insight.
