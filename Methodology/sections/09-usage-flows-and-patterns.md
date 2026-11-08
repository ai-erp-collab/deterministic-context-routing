# Usage Flows And Patterns


## Reader Outcome

After this section, the reader can:

- Explain why usage flows are the bridge between isolated contracts and real ERP behavior.
- Decide when to create a module-specific usage flow and when to create a shared pattern.
- Tell a recipe (a reusable platform technique) from an owner contract (one module's business rule), and give each its home.
- Use the ready-solutions index to find an existing solution before writing a new one.
- Write a usage flow that names steps, actors, calls, data, statuses, checks, side effects, and uncertainty.
- Link usage flows back to module concepts, table contracts, class contracts, source evidence, and open questions.
- Keep scenario documentation small enough to support task intake.

## Core Explanation

Tables explain system state. Class contracts explain reusable behavior. A usage flow explains how those contracts work together in a business scenario.

This distinction matters in proprietary ERP work because real behavior is rarely contained in one file or one table. A user action can depend on document state, access rules, settings, hierarchy rows, formulas, UI hooks, temporary editor tables, workflow transitions, and library calls. If those pieces are documented only as separate contracts, a future agent still has to rediscover the scenario every time.

A usage flow is the curated page for that scenario. It should answer: what starts the flow, which actor or system action runs it, which steps happen in order, which tables are read or written, which contracts are called, which statuses or permissions matter, what messages or errors can appear, and which assumptions remain runtime-unverified.

A pattern is different. A pattern is reusable shape rather than one business scenario. Examples include temp-table editor behavior, status transition handling, access-filter composition, formula evaluation, document posting hooks, or report preparation. If the same shape appears across modules, it belongs in shared knowledge. If it is specific to one module, it belongs near that module's usage flows.

### Recipes And Owner Contracts

Reuse comes in two kinds that look alike and must be kept apart. A recipe is a platform technique: how to do something with the platform itself, such as building a temporary editor table, composing an access filter, or calling a reporting service. Any module can apply it after adapting the parameters. An owner rule is a module's business rule: how this module decides who sees which budget unit, or which statuses allow posting. Another module must not copy it; it calls the owner module's API, as section 08 describes for cross-module rules. A business rule written down as a recipe gets copied into consumers and drifts; a platform technique hidden inside one module's contract gets rediscovered by every other module.

A recipe lives in `knowledge-base/shared/recipes/<domain>/<slug>.md`. Its header records where the technique came from (`donor_file`, `donor_symbol`), a hash of the donor symbol's body (`symbol_hash`), the module that owns the donor code (`owner_module`), and a `status`. Its body states the problem, the signatures, a snippet with module constants replaced by parameters, adaptation notes, and a link to the donor evidence.

A recipe is created only through the promotion rule of section 03: a candidate registered at session close, unchanged for the configured number of later closes, and promoted on the user's yes. The command `kb recipe promote` writes the page and refuses to overwrite an existing recipe. After promotion, the integrity check compares the recorded hash with the donor code and reports drift when the donor changes or disappears, so a recipe never silently describes code that no longer exists.

### The Ready-Solutions Index

Before solving a problem, an agent should know whether the project has already solved it. The ready-solutions index, `knowledge-base/shared/patterns/INDEX.md`, has one row per solution: the task it solves, the pattern or recipe page, and the owner module. It points only to curated shared pages, never into a module's code. When the agent needs to read the donor module's code itself, it asks the user first: the owner module may be under active change, may belong to another team, or may contain rules that must not leak into a consumer.

Usage flows and patterns are context-routing devices. They should not copy large code bodies or raw table exports. They should summarize the scenario and link to deeper evidence only when the current task needs it. Their job is to let a workflow ask, "Which behavior am I changing, which contracts are involved, and what must be checked?"

## Reproducible Procedure

1. Start from a concrete scenario or repeated shape.
   - Create a usage flow when a business action crosses several tables, classes, UI actions, statuses, permissions, formulas, or settings.
   - Create a pattern when the same technical shape appears in multiple scenarios.
   - Do not create a flow only because a method exists; that belongs in a class contract.

2. Choose the right home.
   - Check the ready-solutions index `knowledge-base/shared/patterns/INDEX.md` first; reuse a listed pattern or recipe instead of writing a new one.
   - Put module-specific flows in the active module wiki or the module's established usage area.
   - Put reusable cross-module patterns in shared knowledge.
   - Put a platform technique in a recipe, through the promotion rule; leave a module's business rule in its owner contract and reach it through the owner API.
   - Link from the module concept when the flow is part of the module's baseline behavior or common user intent.

3. Name the flow in business language.
   - Use terms a user would recognize.
   - Add aliases, UI labels, document names, table names, or method names only after the business name is clear.

4. Describe the trigger and scope.
   - State what starts the flow: user action, document event, scheduled job, import, report, workflow transition, or API call.
   - State what is inside the flow and what is explicitly out of scope.

5. Write the ordered behavior.
   - List the main steps in execution order.
   - For each step, name the purpose, involved class contracts, table contracts, UI hooks, formulas, statuses, permissions, or settings.
   - Keep implementation detail only when future work must know it.

6. Record data and side effects.
   - Name important tables read or written.
   - Name persistent changes, temp-table behavior, messages, validations, status changes, access filters, reports, or external calls.
   - State when no persistent side effect is known and that fact matters.

7. Record uncertainty.
   - Separate source-confirmed behavior from inferred behavior.
   - Mark runtime-unverified assumptions about real data, permissions, configuration, UI state, workflow state, or restricted sources.
   - Add the runtime check that would confirm an unresolved claim.

8. Link the flow into the knowledge system.
   - Link module concept terms, table contracts, class contracts, source examples, related flows, shared patterns, and open questions.
   - Keep the page short enough to route context; link out for evidence instead of embedding large evidence.

## Required Artifacts

- Usage flow page for a module-specific scenario, or shared pattern page for reusable cross-module behavior.
- Recipe page `knowledge-base/shared/recipes/<domain>/<slug>.md` with `donor_file`, `donor_symbol`, `symbol_hash`, `owner_module`, and `status`, for each promoted platform technique.
- Ready-solutions index `knowledge-base/shared/patterns/INDEX.md`: task, page, owner module.
- Links to relevant module concept terms.
- Links to table contracts and class contracts involved in the flow.
- Ordered steps with triggers, checks, data, side effects, statuses, and errors when known.
- Confidence labels and runtime-unverified assumptions.
- Related notes or index updates that make the flow discoverable.

## Example

A budgeting task asks why one user sees a child budget unit but not the parent unit.

A table contract can describe the hierarchy fields. A class contract can describe the access helper. Neither one alone explains the scenario. The usage flow should describe the access path:

- the user opens the budgeting screen or report;
- the module resolves the user's department or role;
- the access helper reads hierarchy and access-scope tables;
- the flow applies active dates, parent-child relations, and permission filters;
- the UI or report receives the filtered budget context;
- missing setup or inactive hierarchy rows produce an empty or partial result;
- real permissions and data configuration are runtime-unverified unless observed.

That flow lets the next task start from the scenario. The agent can then follow links to the hierarchy table contract, the access helper contract, the module concept, and the verification notes instead of rediscovering the behavior from raw source and schema exports.

## Failure Modes

- Treating a usage flow as a code summary: the business scenario disappears.
- Treating a method contract as a flow: the page misses the surrounding tables, statuses, UI actions, and permissions.
- Treating a repeated pattern as module-specific: reusable platform knowledge gets trapped in one module.
- Copying large source fragments or table exports into the flow.
- Omitting side effects, validations, messages, statuses, or permissions.
- Hiding runtime uncertainty behind confident prose.
- Leaving the flow unlinked from module terms, table contracts, and class contracts.
- Writing a module's business rule as a recipe: consumers copy it and the copies drift from the owner.
- Promoting a technique the moment it first works: the shared recipe describes code that is still changing.
- Pointing the ready-solutions index into module code: consumers start reading and copying another module's internals.
- Ignoring recipe drift reports: the recipe describes a donor that changed or no longer exists.

## Assumptions And Runtime Limits

- A usage flow can start partial when uncertainty is explicit.
- Static source and schema evidence can identify possible flow steps, but real data, configuration, permissions, UI state, and workflow state may still be needed.
- A shared pattern should be generalized only after there is enough evidence that the shape repeats.
- A usage flow is an entry point for task work, not a replacement for deeper source review when implementation detail matters.

## Related Notes

- `05-module-concept-and-language.md`: defines module terms and intent patterns that should link to important flows.
- `07-tables-as-contracts.md`: defines the data contracts used inside flows.
- `03-knowledge-system.md`: defines the promotion rule with a cooldown that creates recipes.
- `08-libraries-and-class-contracts.md`: defines the behavior contracts used inside flows and the owner API for cross-module rules.
- `10-agentic-workflow-with-superpowers.md`: downstream section for using flows during disciplined agent task work.
