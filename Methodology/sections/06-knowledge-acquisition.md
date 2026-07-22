# Knowledge Acquisition


## Reader Outcome

After this section, the reader can:

- Identify which sources may be used for a proprietary ERP knowledge task.
- Distinguish raw evidence from curated knowledge.
- Classify findings as confirmed, inferred, runtime-unverified, or blocked-by-access.
- Respect access and licensing limits when using platform libraries or other protected sources.
- Convert discoveries into module wiki pages, shared wiki pages, table contracts, class contracts, usage flows, and open questions.

## Core Explanation

The module concept tells the agent what the business area means. Knowledge acquisition tells the agent how to fill gaps in that understanding without pretending that every source is equally available, reliable, or confirmed.

In proprietary ERP work, important knowledge is distributed. A behavior may be visible through a table schema, a class contract, a source example, a user document, a configuration export, a previous design, or a runtime observation. No single source is enough for every task.

Knowledge acquisition is the controlled conversion of evidence into usable context. It is not "read everything." It is not "trust the first search result." It is a procedure for finding the smallest evidence needed, recording how reliable it is, and placing the resulting knowledge in the right memory layer.

Common source types include:

- existing module wiki and shared wiki pages;
- module concept pages, table pages, contract pages, and usage pages;
- project libraries and module source examples;
- platform libraries, when the project has access and the license or project rules allow that use;
- exported table schemas and recognized CSV, XML, TXT, or similar artifacts;
- user documentation and business requirements;
- previous designs, plans, review notes, and session-state entries;
- runtime observations from the proprietary ERP environment when available.

The access and licensing rule matters. If platform libraries are unavailable, restricted, or outside the allowed project use, they are not an evidence source for the task. The agent should use permitted evidence, record the gap, and avoid presenting assumptions about inaccessible internals as confirmed facts.

The order also matters. Curated knowledge is usually the cheapest entry point. Raw evidence is the ground for claims, but it is often too large or too noisy for task intake. A table export may prove a field exists, but a table page should explain what the field means. A source example may show a method call, but a contract page should explain what consumers can rely on.

For that reason, acquisition has two outputs:

- immediate task context: the minimal facts, files, assumptions, and examples needed now;
- durable memory: updated wiki, contracts, usage flows, artifact indexes, open questions, and session-state notes.

Uncertainty is part of the output. Static source evidence can prove that code exists. It may not prove how the behavior works with real configuration, data, permissions, UI state, or workflow status. Runtime behavior should be marked with the `runtime-confirmed` qualifier (defined below) only when it was actually observed in the target environment.

Use the following confidence labels:

- confirmed: directly supported by permitted source evidence, recognized schema, user-approved requirement, or verified runtime behavior;
- inferred: logically derived from evidence, but not directly stated or executed;
- runtime-unverified: static evidence exists, but behavior still needs confirmation in the proprietary runtime;
- blocked-by-access: a likely source exists, but access, license, project policy, or environment limits prevent using it.

`confirmed` is not one flat state. A claim can be confirmed at one evidence layer without being confirmed at another, so `confirmed` takes an optional evidence-layer qualifier:

- schema-confirmed: the field, table, method, or structure exists in recognized structural evidence, such as an exported schema, independent of business meaning or runtime behavior;
- runtime-confirmed: the behavior was actually observed in the target proprietary runtime, not only inferred from static evidence.

A fact can be schema-confirmed while its business meaning is still inferred and its behavior is still runtime-unverified. Do not let one qualified confirmation upgrade the whole claim to plain `confirmed`. Use the unqualified `confirmed` label only when the claim holds at every evidence layer the current task depends on.

These labels classify claims, not whole pages. A table page, contract page, or usage flow can have `status: partial` while individual facts inside it are labeled `confirmed` (optionally qualified as `schema-confirmed` or `runtime-confirmed`), `inferred`, `runtime-unverified`, or `blocked-by-access`. `partial` is a page-level completeness state; it is never used as a claim-level confidence label. This keeps the page usable before it is complete without letting one confirmed field make the whole business interpretation look confirmed.

These labels keep the agent honest. They also help future work: a runtime-unverified note can become confirmed after a later check, and a blocked-by-access note prevents repeated attempts to use a source that the project should not read.

## Reproducible Procedure

1. Start from the task and module concept.
   - Identify the active module, business terms, boundaries, and likely technical objects.
   - Name the exact knowledge gap before searching.

2. Search curated memory first.
   - Check module concept, module wiki, shared wiki, table pages, contract pages, usage pages, decisions, and open questions.
   - Prefer the smallest relevant page over broad source reading.

3. Inspect permitted source evidence when curated memory is missing or insufficient.
   - Use project libraries and module source examples when they are part of the workspace.
   - Use platform libraries only when access exists and license or project rules allow that use.
   - Use recognized table exports and artifact indexes for schema and table-contract questions.
   - Use user documentation and business requirements for intended behavior.
   - Use runtime observations only when the target environment is actually available.

4. Record source provenance at a useful level.
   - Link to the source file, artifact, wiki page, or observation note.
   - Avoid pasting large source bodies into wiki pages.
   - Summarize what the evidence supports and what it does not support.

5. Classify each finding.
   - Use confirmed, inferred, runtime-unverified, or blocked-by-access.
   - Do not upgrade an inference into a confirmed rule.
   - If runtime behavior is assumed, say what runtime check would confirm it.

6. Convert repeated or durable findings into curated memory.
   - Module-specific behavior goes to the active module wiki.
   - Reusable platform or cross-module behavior goes to shared wiki.
   - Table semantics go to table pages.
   - Public class or method behavior goes to contract pages.
   - Multi-object scenarios go to usage pages.
   - Open questions stay visible until resolved.

7. Maintain artifact lifecycle when new exports are found.
   - Put newly found XML, CSV, TXT, or similar table/source exports in the raw artifact area.
   - Recognize and review the artifact before treating it as curated knowledge.
   - Move processed artifacts only after related wiki pages are created or refreshed.
   - Update the artifact index.

8. Feed the current task with bounded context.
   - Bring forward only the facts needed for design, implementation, or verification.
   - Link to deeper evidence instead of loading broad dumps.
   - Record remaining assumptions in the design, plan, wiki, or session state.

## Required Artifacts

- A named knowledge gap or research question.
- Links to the curated pages checked first.
- Links to permitted source evidence inspected.
- Confidence label for each important finding.
- Open questions for unresolved or inaccessible facts.
- Updated module wiki, shared wiki, table page, contract page, usage page, or artifact index when the finding is durable.
- Session-state note when acquisition changes current task context or leaves important verification limits.

## Example

A task needs to know whether a budget access rule should use the user's department, the parent budget unit, or both.

The acquisition path should be bounded:

- start from the budgeting module concept and identify the terms: user department, leaf department, parent budget unit, access scope;
- check existing module wiki pages for budget hierarchy, access flows, and table contracts;
- inspect project source examples or module libraries that implement access checks;
- inspect recognized table exports for hierarchy and group relations when table semantics are unclear;
- use platform libraries only if the workspace has access and the license or project rules allow that inspection;
- record whether the final mapping is confirmed by source evidence, inferred from examples, or runtime-unverified because real hierarchy records and permission setup were not available.

The durable output might be a refreshed usage page for budget access, a table note about hierarchy fields, an open question about runtime configuration, and a short session-state note that the implementation still needs runtime validation.

## Failure Modes

- Reading raw source before checking curated memory: the task becomes larger than necessary.
- Treating inaccessible platform libraries as assumed knowledge: the agent invents behavior it is not allowed or able to inspect.
- Ignoring license or project access limits: evidence use becomes unsafe even if technically possible.
- Treating static evidence as runtime confirmation: behavior may still fail under real data, rights, configuration, or workflow state.
- Keeping discoveries only in chat: the next task repeats the acquisition.
- Overloading wiki pages with raw dumps: curated memory becomes too expensive to use.
- Storing module-specific findings in shared memory: local behavior becomes overgeneralized.
- Storing reusable platform behavior in one module: other modules rediscover it.
- Leaving uncertainty unlabeled: future readers cannot tell what is known and what is assumed.

## Assumptions And Runtime Limits

- This method assumes the agent can read local curated memory and permitted workspace evidence.
- Platform-library inspection is conditional on access and license or project-rule permission.
- Some proprietary runtime behavior cannot be verified statically.
- A finding can be useful before it is complete, but its confidence label must stay attached to it.
- If a source cannot be used, the task should proceed from allowed evidence or record a blocked-by-access gap.

## Related Notes

- `01-why-this-method-exists.md`: explains why proprietary ERP work is a context-management problem.
- `03-knowledge-system.md`: defines memory layers and source evidence.
- `05-module-concept-and-language.md`: defines the business-language entry point for acquisition.
- `07-tables-as-contracts.md`: downstream section for converting table evidence into durable contracts.
- `08-libraries-and-class-contracts.md`: downstream section for documenting public behavior from source evidence.
- `Methodology/Wiki/insights.md`: records runtime uncertainty and tables-as-contracts as core insights.
