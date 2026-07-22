# KB Curator And Artifact Workflow


## Reader Outcome

After this section, the reader can:

- Explain why a knowledge curator is useful in proprietary ERP work.
- Use a curator workflow to convert raw evidence into table, contract, usage, and pattern pages.
- Separate confirmed facts, inferred meaning, runtime-unverified behavior, and blocked evidence.
- Maintain raw-to-processed artifact lifecycle.
- Decide which curator instructions are universal and which are project-specific.

## Core Explanation

The workspace template gives the agent places to put knowledge. The curator workflow explains how knowledge gets there.

In proprietary ERP work, source evidence is often large, uneven, and expensive to read: exported table schemas, platform libraries, project libraries, usage examples, user documentation, runtime observations, and source artifacts. A task agent should not repeatedly rediscover the same API shape or table meaning. A curator converts evidence into compact pages that future agents can search cheaply.

This project uses a `kb-curator` skill for that purpose. Its important universal ideas are:

- search existing knowledge first;
- inspect raw evidence only when curated knowledge is missing;
- write the smallest useful page;
- update indexes;
- preserve uncertainty instead of speculating;
- keep pages optimized for agent lookup, not polished human prose.

The exact source roots are project-specific. In this project, platform or project libraries and usage examples have established folders. Another team may use API docs, source repositories, database exports, logs, or runtime observations instead.

## Curator Instruction Template

A generic curator instruction can look like this:

```markdown
# KB Curator

## Goal

Maintain an agent-first knowledge base for cheap lookup of contracts, functions, tables, usage flows, and patterns.

## Sources

- `<contract-source-root>/`: source evidence for APIs, libraries, or platform behavior.
- `<usage-source-root>/`: examples of project usage and integration conventions.
- `<artifact-root>/`: exported schemas, reports, or other source artifacts.
- `<knowledge-root>/`: durable curated knowledge produced from evidence.

## Workflow

1. Search curated knowledge first.
2. If the answer is missing, inspect the smallest relevant source evidence.
3. Create or update one focused page.
4. Link related contracts, tables, usage flows, patterns, and source evidence.
5. Update affected `INDEX.md` files.
6. Mark uncertainty explicitly.
```

Then add project-specific rules:

```markdown
## Project-Specific Rules

- Example: Use the project's parser for `<TABLE_EXPORT_FORMAT>` artifacts.
- Example: Preserve source artifact encoding; do not rewrite raw exports.
- Example: Use neutral evidence wording when source-origin details are sensitive.
- Example: When runtime testing is unavailable, record static checks and runtime-unverified assumptions.
```

## Page Families

The curator should create or update these page families:

- module concept pages: business purpose, boundaries, terms, intent patterns;
- table pages: keys, important fields, business meanings, codes, related tables, used-by links;
- contract pages: public shape, inputs, outputs, side effects, runtime assumptions;
- usage pages: scenario flow, calls, tables, contracts, caveats;
- pattern pages: repeated cross-module or module-specific technical shapes;
- indexes: short navigation pages with aliases and high-signal links.

These match the starter templates from the previous section. If a guide names a page family, the starter kit should include a template or explain why that page family is optional.

## Artifact Lifecycle

Use a strict raw-to-curated-to-processed workflow:

1. Put newly found exports in the raw artifact area.
2. Identify format and encoding before parsing.
3. Parse with a structured parser when possible.
4. Review generated pages for extraction errors.
5. Add business meaning, links, and uncertainty labels.
6. Update indexes and artifact ledger.
7. Move artifacts to processed only after related curated pages are created or refreshed.
8. Record the result and remaining assumptions in session state.

Raw artifacts are evidence. Curated pages are the working memory. Processed artifacts are evidence that has already been recognized and connected.

The lifecycle is iterative. A processed artifact can be superseded by a newer export, a runtime observation can correct a static inference, and a task can reveal that a page is too broad or too vague for lookup. The curator should revise the smallest affected pages, preserve the evidence trail, and record whether the old claim was confirmed, narrowed, corrected, or left runtime-unverified. Revision is not a failure of curation; it is how static evidence becomes reliable working memory.

## Reproducible Procedure

1. Start with a knowledge need.
   - Name the task, module, table, class, scenario, or user term that requires knowledge.
   - Avoid normalizing evidence only because it exists.

2. Search cheaply.
   - Search the module wiki, shared wiki, indexes, and existing contracts first.
   - Use exact names, aliases, business terms, and likely abbreviations.

3. Inspect the smallest relevant evidence.
   - Use source roots, examples, table exports, or runtime notes according to project rules.
   - Prefer structured parsers for structured artifacts.
   - Read only what is needed for the current page.

4. Write or update the smallest useful page.
   - Use the matching template.
   - Summarize behavior and meaning.
   - Link to evidence instead of copying large source bodies.

5. Connect the page.
   - Update `INDEX.md` files.
   - Add aliases and related links.
   - Link from module concept, table contracts, class contracts, or usage flows when relevant.

6. Preserve uncertainty.
   - Use page `status` for completeness, such as `partial` when the page is useful but not finished.
   - Use claim `confidence` for evidence strength: `confirmed`, `inferred`, `runtime-unverified`, or `blocked-by-access`.
   - Mark runtime-unverified behavior separately from source-confirmed structure.
   - State the check that would resolve the uncertainty.

7. Revise prior knowledge when evidence changes.
   - Find existing pages that cite or depend on the artifact, table, contract, or scenario.
   - Update only the smallest affected pages and indexes.
   - Mark superseded interpretations instead of silently deleting useful history.
   - Keep the session-state note focused on changed pages and remaining assumptions.

8. Complete artifact bookkeeping.
   - Move recognized raw artifacts to processed only after curated pages are refreshed.
   - Update the artifact index.
   - Update session state with what changed and what remains unknown.

## Required Artifacts

- Curated wiki page or explicit note that no durable page was needed.
- Updated index for any folder that gained or changed a page.
- Source artifact index entry when artifacts are introduced or processed.
- Links between table, contract, usage, pattern, and module concept pages.
- Session-state note for non-conversational curation.
- Verification note for parser/static checks and unresolved runtime assumptions.
- Revision note when new evidence changes an existing curated page.

## Example

A project receives a table export for budget hierarchy and a task asks about access to parent budget units.

The curator should not paste the export into a wiki page. It should:

- put the export in the raw artifact folder;
- identify encoding and format;
- parse it with a structured parser if one exists;
- create or refresh the table contract for the hierarchy table;
- add aliases such as budget unit, parent unit, and hierarchy;
- link the table to the access helper contract and access usage flow;
- mark business meaning as partial if only field names support it;
- move the artifact to processed only after the table page and index are updated;
- record remaining runtime assumptions, such as real permission setup or active-date behavior.

This produces a small route for future agents: user term -> module concept -> usage flow -> table and contract pages -> source artifact.

## Failure Modes

- Reading raw evidence before checking existing curated knowledge.
- Generating pages with no links or indexes.
- Treating extracted field names as confirmed business meaning.
- Moving artifacts to processed before curated pages are reviewed.
- Adding new evidence without checking whether old curated pages need revision.
- Copying large source bodies into wiki pages.
- Creating polished prose that is too long for task intake.
- Spending tokens on speculation instead of marking uncertainty.
- Letting project-specific parsers or source roots appear universal in a published guide.

## Assumptions And Runtime Limits

- A curator can make static evidence cheap to use, but cannot prove every runtime behavior.
- Some evidence may be blocked by access, license, environment, or runtime availability.
- Generated pages require review; parser output is not automatically durable knowledge.
- Another project can replace this project's `kb-curator` with scripts, human review, or another tool if it preserves the same evidence discipline.

## Related Notes

- `06-knowledge-acquisition.md`: defines evidence and uncertainty.
- `07-tables-as-contracts.md`: defines table contracts.
- `08-libraries-and-class-contracts.md`: defines behavior contracts.
- `09-usage-flows-and-patterns.md`: defines scenario and pattern pages.
- `12-practical-workspace-template.md`: defines the starter workspace and templates.
- `14-adoption-bootstrap-and-template-audit.md`: downstream section for team adoption and template audit.
