# KB Curator And Artifact Workflow


## Reader Outcome

After this section, the reader can:

- Explain why a knowledge curator is useful in proprietary ERP work.
- Use a curator workflow to convert raw evidence into table, contract, usage, and pattern pages.
- Separate confirmed facts, inferred meaning, runtime-unverified behavior, and blocked evidence.
- Maintain the raw-to-processed artifact lifecycle as registry statuses, without moving files.
- Register evidence as a hashed copy and prove that every evidence file is tracked.
- Work the numbered issue queue that the integrity checks produce.
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

Evidence enters the workspace as a copy. The command `kb ingest <path...> --module <Module>` copies each file into `source-artifacts/<kind>/raw/<module>/` and records a row in the evidence registry `source-artifacts/registry.json`: the copy's path, the origin path, the module, the kind, a SHA-256 hash, the status, the curated pages built from it, and when it was first seen. The copy, not the origin, is what pages link to, because the origin may sit on another machine or change without notice. The registry is the source of truth; `source-artifacts/INDEX.md` is generated from it as a compact list for agents to read.

Use a strict raw-to-curated-to-processed workflow:

1. Register newly found evidence with `kb ingest`; do not copy it by hand.
2. Identify format and encoding before parsing.
3. Parse with a structured parser when possible (for table exports, `kb table`, section 07).
4. Review generated pages for extraction errors.
5. Add business meaning, links, and uncertainty labels.
6. Update indexes. Name the evidence copy in the curated page's `source:` line.
7. Let the integrity check mark the registry row `processed`: it does so only when a curated page that names the copy exists. Files stay where they are; `raw` and `processed` are statuses, not folders.
8. Record the result and remaining assumptions in session state.

Raw artifacts are evidence. Curated pages are the working memory. Processed artifacts are evidence that has already been recognized and connected. Two more statuses exist: `reference` for evidence kept for lookup without its own page, and `ignored` for files deliberately not curated.

Tracking is complete by construction. Every file under the evidence folders named in `modules.md` and under `source-artifacts/` must have a registry row unless `.kb/track.ignore` excludes it. A file without a row is a blocking issue, because a session that does not know the file exists will either miss it or parse it again from scratch. The integrity check also compares each origin's current hash with the registered one: a changed origin means a new version arrived and the affected pages need revision, which is a curation decision, so the check reports it and changes nothing. Rows still `raw` are listed as a backlog of evidence waiting to be curated.

### The Issue Queue

Everything the checks find and cannot fix safely goes into one numbered queue. Each full `kb check` leaves a report named by date under `docs/checks/` and replaces `docs/checks/OPEN.md` with the list of every open issue (id, severity, module, symptom, proposed fix), and keeps a one-line health pointer in `known_issues.md`. The edit hook prints the issues on the file just changed, and the end-of-turn hook only the ones the session introduced, each with its queue id when one exists. The curator works the queue in order: run `kb fix --safe` first (fixes with one correct answer, journaled), then take blocking issues before minor ones, apply an agreed proposed fix with `kb fix --ids <N>`, and settle the rest by editing pages or asking the user when the answer is about meaning. An issue never disappears by being ignored; it disappears when the next full check no longer finds it, and the report lists it as resolved.

The lifecycle is iterative. A processed artifact can be superseded by a newer export, a runtime observation can correct a static inference, and a task can reveal that a page is too broad or too vague for lookup. The curator should revise the smallest affected pages, preserve the evidence trail, and record whether the old claim was confirmed, narrowed, corrected, or left runtime-unverified. Revision is not a failure of curation; it is how static evidence becomes reliable working memory.

## Reproducible Procedure

1. Start with a knowledge need.
   - Name the task, module, table, class, scenario, or user term that requires knowledge.
   - Avoid normalizing evidence only because it exists.

2. Search cheaply.
   - Search the module wiki, shared wiki, indexes, and existing contracts first; `kb resolve <name>` looks up names, aliases, and glossary terms in one step.
   - Use exact names, aliases, business terms, and likely abbreviations.

3. Inspect the smallest relevant evidence.
   - Use source roots, examples, table exports, or runtime notes according to project rules.
   - Register new evidence with `kb ingest` before using it.
   - Prefer structured parsers for structured artifacts.
   - Open a large source file through `kb outline` and read only the needed symbols.
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
   - Name the evidence copy in the page's `source:` line so the registry row becomes `processed`; never move the file.
   - Run `kb check --changed <files>` and resolve what it lists, or leave the issues numbered in the queue with a note.
   - Update session state with what changed and what remains unknown.

## Required Artifacts

- Curated wiki page or explicit note that no durable page was needed.
- Updated index for any folder that gained or changed a page.
- Evidence registry row for every evidence file, created by `kb ingest`; generated `source-artifacts/INDEX.md`.
- `.kb/track.ignore` entries for files deliberately excluded from tracking.
- Issue report in `docs/checks/` and the open queue `docs/checks/OPEN.md`.
- Links between table, contract, usage, pattern, and module concept pages.
- Session-state note for non-conversational curation.
- Verification note for parser/static checks and unresolved runtime assumptions.
- Revision note when new evidence changes an existing curated page.

## Example

A project receives a table export for budget hierarchy and a task asks about access to parent budget units.

The curator should not paste the export into a wiki page. It should:

- register the export with `kb ingest`, which copies it, hashes it, and records it as `raw`;
- identify encoding and format;
- parse it with a structured parser if one exists;
- create or refresh the table contract for the hierarchy table;
- add aliases such as budget unit, parent unit, and hierarchy;
- link the table to the access helper contract and access usage flow;
- mark business meaning as partial if only field names support it;
- name the export copy in the table page's `source:` line, so the check marks the registry row `processed` once the page and index are updated;
- record remaining runtime assumptions, such as real permission setup or active-date behavior.

This produces a small route for future agents: user term -> module concept -> usage flow -> table and contract pages -> source artifact.

## Failure Modes

- Reading raw evidence before checking existing curated knowledge.
- Generating pages with no links or indexes.
- Treating extracted field names as confirmed business meaning.
- Marking artifacts processed before curated pages are reviewed.
- Copying evidence into the workspace by hand: the file has no registry row, the next session does not know it exists, and the completeness check blocks.
- Moving evidence files between folders: every link to the copy breaks.
- Re-ingesting an origin silently after it changed: pages built on the old version are not revised.
- Treating the issue queue as optional: open issues accumulate until the routes they describe stop working.
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
- Hash comparison detects that an origin changed, not what changed; deciding which pages to revise stays with the curator.

## Related Notes

- `06-knowledge-acquisition.md`: defines evidence and uncertainty.
- `07-tables-as-contracts.md`: defines table contracts.
- `08-libraries-and-class-contracts.md`: defines behavior contracts.
- `09-usage-flows-and-patterns.md`: defines scenario and pattern pages.
- `03-knowledge-system.md`: defines knowledge-base degradation and the integrity layer that produces the issue queue.
- `12-practical-workspace-template.md`: defines the starter workspace and templates.
- `14-adoption-bootstrap-and-template-audit.md`: downstream section for team adoption and template audit.
