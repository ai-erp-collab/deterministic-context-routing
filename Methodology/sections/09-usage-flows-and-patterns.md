# Usage Flows And Patterns


## Reader Outcome

After this section, the reader can:

- Explain why usage flows are the bridge between isolated contracts and real ERP behavior.
- Decide when to create a module-specific usage flow and when to create a shared pattern.
- Write a usage flow that names steps, actors, calls, data, statuses, checks, side effects, and uncertainty.
- Link usage flows back to module concepts, table contracts, class contracts, source evidence, and open questions.
- Keep scenario documentation small enough to support task intake.

## Core Explanation

Tables explain system state. Class contracts explain reusable behavior. A usage flow explains how those contracts work together in a business scenario.

This distinction matters in proprietary ERP work because real behavior is rarely contained in one file or one table. A user action can depend on document state, access rules, settings, hierarchy rows, formulas, UI hooks, temporary editor tables, workflow transitions, and library calls. If those pieces are documented only as separate contracts, a future agent still has to rediscover the scenario every time.

A usage flow is the curated page for that scenario. It should answer: what starts the flow, which actor or system action runs it, which steps happen in order, which tables are read or written, which contracts are called, which statuses or permissions matter, what messages or errors can appear, and which assumptions remain runtime-unverified.

A pattern is different. A pattern is reusable shape rather than one business scenario. Examples include temp-table editor behavior, status transition handling, access-filter composition, formula evaluation, document posting hooks, or report preparation. If the same shape appears across modules, it belongs in shared knowledge. If it is specific to one module, it belongs near that module's usage flows.

Usage flows and patterns are context-routing devices. They should not copy large code bodies or raw table exports. They should summarize the scenario and link to deeper evidence only when the current task needs it. Their job is to let a workflow ask, "Which behavior am I changing, which contracts are involved, and what must be checked?"

## Reproducible Procedure

1. Start from a concrete scenario or repeated shape.
   - Create a usage flow when a business action crosses several tables, classes, UI actions, statuses, permissions, formulas, or settings.
   - Create a pattern when the same technical shape appears in multiple scenarios.
   - Do not create a flow only because a method exists; that belongs in a class contract.

2. Choose the right home.
   - Put module-specific flows in the active module wiki or the module's established usage area.
   - Put reusable cross-module patterns in shared knowledge.
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

## Assumptions And Runtime Limits

- A usage flow can start partial when uncertainty is explicit.
- Static source and schema evidence can identify possible flow steps, but real data, configuration, permissions, UI state, and workflow state may still be needed.
- A shared pattern should be generalized only after there is enough evidence that the shape repeats.
- A usage flow is an entry point for task work, not a replacement for deeper source review when implementation detail matters.

## Related Notes

- `05-module-concept-and-language.md`: defines module terms and intent patterns that should link to important flows.
- `07-tables-as-contracts.md`: defines the data contracts used inside flows.
- `08-libraries-and-class-contracts.md`: defines the behavior contracts used inside flows.
- `10-agentic-workflow-with-superpowers.md`: downstream section for using flows during disciplined agent task work.
