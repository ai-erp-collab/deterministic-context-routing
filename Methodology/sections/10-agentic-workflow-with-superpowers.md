# Agentic Workflow With Superpowers


## Reader Outcome

After this section, the reader can:

- Explain why this methodology should not duplicate a third-party agent workflow framework.
- Describe what proprietary ERP context must be supplied before an agent begins task work.
- Use a workflow framework such as Superpowers for task intake, design, planning, implementation, and verification.
- Keep this methodology focused on ERP knowledge: module language, contracts, flows, uncertainty, and documentation updates.

## Core Explanation

The previous sections define the knowledge layer needed for proprietary ERP work: module concepts, table contracts, class contracts, usage flows, source evidence, confidence labels, and context-routing rules. They explain what the agent must know.

They should not also pretend to own the full agent work lifecycle. Task intake, brainstorming, design, planning, implementation loops, code review, and verification gates are already the responsibility of disciplined agent workflow systems. In this workspace, that role is played by Superpowers.

The methodology should therefore make a narrow claim:

- use this methodology to build and maintain the ERP knowledge layer;
- use Superpowers, or an equivalent disciplined workflow, to run the task lifecycle;
- connect the two by giving the workflow the right module context, contracts, usage flows, assumptions, and verification limits.

This matters because copying an external workflow into the methodology creates two problems. First, it blurs authorship and maintenance responsibility. Second, it makes the book stale when the workflow framework changes. A better design is to document the integration boundary.

At task start, the ERP layer answers: which module is active, which business terms matter, which usage flows and contracts are relevant, which runtime conditions are uncertain, and which documentation may need to change. The external workflow then decides how to brainstorm, design, plan, implement, verify, and finish the work.

The output of a task is not only code. In proprietary ERP work, a task is complete only when the behavior, contracts, usage notes, verification record, and restart context do not contradict each other.

## Reproducible Procedure

1. Resolve the active module.
   - Use workspace rules, module registry, explicit user request, or latest session state.
   - If the module is ambiguous and cannot be inferred safely, ask a focused question.

2. Load the smallest useful ERP context.
   - Read the module concept first.
   - Follow links only to relevant table contracts, class contracts, usage flows, open questions, and source evidence.
   - Respect stop markers and context-routing instructions.

3. Translate the user request into module language.
   - Name the business terms in the request.
   - Map terms to likely tables, classes, settings, statuses, UI actions, formulas, permissions, and usage flows.
   - Mark ambiguous terms instead of guessing silently.

4. Hand the task lifecycle to the workflow framework.
   - Use Superpowers or an equivalent disciplined process for brainstorming, design, planning, implementation, debugging, review, and verification.
   - Do not rewrite the framework's detailed steps in this methodology.
   - Treat the framework as the process layer and this methodology as the ERP knowledge layer.

5. Carry ERP-specific context through the workflow.
   - Designs and plans should name affected module terms, tables, contracts, flows, rights, statuses, runtime assumptions, and documentation updates.
   - Implementation should update contracts or usage pages when public behavior or important module rules change.
   - Verification should distinguish static checks, runtime checks, blocked-by-access gaps, and runtime-unverified assumptions.

6. Record the outcome.
   - Update durable knowledge when the task changes or clarifies behavior.
   - Update session state with what changed, what was checked, and what remains uncertain.
   - Keep detailed task lifecycle artifacts in the workflow's normal location.

## Required Artifacts

- Active module decision.
- Minimal context set: module concept plus relevant contracts, flows, open questions, or source evidence.
- Workflow artifacts produced by Superpowers or the chosen equivalent process.
- Updated table contract, class contract, usage flow, module concept, or documentation layer when durable ERP knowledge changes.
- Verification record that separates confirmed facts from runtime-unverified or blocked-by-access assumptions.
- Session-state note for restart context.

## Example

A user asks: "Make budget access respect the parent unit."

The methodology does not prescribe every step of the design and implementation workflow. It first prepares the ERP context:

- active module: budgeting;
- module terms: budget unit, parent unit, access scope, user department;
- likely evidence: module concept, budget hierarchy table contracts, access helper contracts, access usage flow, open questions about runtime configuration;
- likely risks: rights, active periods, hierarchy depth, missing setup, runtime data;
- documentation impact: table contract or access usage flow may need refresh.

After that, Superpowers or an equivalent workflow should drive the task: clarify scope, write the design, plan the implementation, make the change, verify it, and finish the branch or task record. The ERP methodology remains responsible for making sure the workflow receives the right proprietary context and writes durable ERP knowledge back when behavior changes.

## Failure Modes

- Rewriting a third-party workflow as if it were part of this methodology.
- Starting implementation before the active module and key business terms are mapped.
- Loading raw source evidence before checking curated module concepts, contracts, and flows.
- Treating static source review as runtime confirmation.
- Updating code while leaving changed table, class, or usage contracts stale.
- Recording task decisions only in chat history.
- Letting the workflow framework replace ERP understanding instead of using it to structure the work.

## Assumptions And Runtime Limits

- Superpowers is recommended because it is available in this workspace and already provides a disciplined task lifecycle.
- Another workflow can replace Superpowers if it enforces comparable intake, design, planning, implementation, verification, and completion gates.
- This methodology should name the integration boundary, not copy external workflow instructions.
- Proprietary ERP runtime behavior may still require real data, permissions, configuration, UI state, or environment access to verify.

## Related Notes

- `05-module-concept-and-language.md`: defines the business-language entry point for task work.
- `07-tables-as-contracts.md`: defines table contracts used during task scoping.
- `08-libraries-and-class-contracts.md`: defines behavior contracts used during task scoping.
- `09-usage-flows-and-patterns.md`: defines scenario pages that connect contracts into business behavior.
- `11-how-emergent-capabilities-work.md`: downstream section mapping this workflow's mechanisms to the capabilities they produce.
- `12-practical-workspace-template.md`: downstream section for deciding where resulting knowledge belongs in a starter workspace.
