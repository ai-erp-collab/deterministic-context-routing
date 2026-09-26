# Agentic Workflow With Superpowers


## Reader Outcome

After this section, the reader can:

- Explain why this methodology should not duplicate a third-party agent workflow framework.
- Describe what proprietary ERP context must be supplied before an agent begins task work.
- Use a workflow framework such as Superpowers for task intake, design, planning, implementation, and verification.
- Keep this methodology focused on ERP knowledge: module language, contracts, flows, uncertainty, and documentation updates.
- Extend a task from the active module into another module on request, with a fixed lookup order, a clear line between looking and changing, and a mark left in the other module.

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

### Cross-Module Work From One Module

Work runs in one active module. Sooner or later a task in that module needs a rule that was already built in another module: which documents a user may see, how a hierarchy is walked, which status a route allows. A separate shared library for that rule would be the wrong architecture, because the rule still belongs to one business domain. The right move is to use the module that owns the rule and, when needed, extend it. `08-libraries-and-class-contracts.md` calls it the **owner module**, and the module where the task started the **consumer module**; the owner exposes the rule through an **owner API**.

The agent does not leave the active module on its own initiative. Cross-module work starts only from the user, in one of two forms:

- a **question**, such as "do we already have user access rules for documents somewhere?" The agent looks, reports where the rule lives and how the consumer could call it, and changes no code in the owner module;
- a **command**, such as "look at module Alpha and add a helper there for this" or "reuse what Alpha already has." The agent may then change the owner module within the scope of the command.

The lookup is deterministic and uses only what the workspace already has. First, the consumer's own knowledge base and instructions: an earlier task may already have left a link to the owner. Next, if the user named the module, go straight to that module's knowledge-base `INDEX.md`. Otherwise, resolve the candidate owner through the module registry (`modules.md`) and then its `INDEX.md` and contract pages. Code in the owner's source roots is read only when its knowledge base lacks the fact, as elsewhere in this method.

Two records keep the result from being lost. The first is a **link in the consumer**: once the owner rule is taken into work, the consumer's knowledge base, its module instructions, or both get a short link to the owner contract page, so the next task starts from the owner API instead of searching again. A plain lookup question leaves no link, because the user may have asked for reasons unrelated to the consumer module. The second is a **mark in the owner**: any write into the owner module, whether code or knowledge, is recorded in the owner module itself. Without it, the next session that opens the owner module sees changed code and no explanation of what changed, for whom, or why.

The mark has two layers. The owner's `session_state.md` receives a cross-module entry that names the consumer module, the change, the reason, and the request that allowed it. Because an agent reads only the latest entry, that entry must copy the owner's own previous next action word for word; otherwise a foreign entry silently replaces the owner's restart point. The owner contract page receives the durable part: the consumer in its consumer list and one line in its change history that says what changed and why.

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

4. Extend to another module only on request.
   - Start cross-module work only from a user question or command; a question allows looking, a command allows changing the owner module.
   - Look up the owner in a fixed order: links already present in the consumer's knowledge base or instructions, then the module the user named, then the module registry; then the owner's `INDEX.md` and contract pages; then owner source code only when the knowledge base lacks the fact.
   - Before writing into the owner module, read its module instructions and apply them to its files.
   - Implement the rule behind an owner API, as described in `08-libraries-and-class-contracts.md`, and leave only an adapter in the consumer.
   - Once the owner rule is taken into work (a command, or the user decides to reuse it), leave a link to the owner contract page in the consumer's knowledge base and, if the rule should guide every future task there, in its module instructions. A plain question leaves no link.
   - For every write into the owner module, add the cross-module entry to the owner's `session_state.md` with the owner's previous next action carried over unchanged, and update the owner contract page's consumer list and change history.

5. Hand the task lifecycle to the workflow framework.
   - Use Superpowers or an equivalent disciplined process for brainstorming, design, planning, implementation, debugging, review, and verification.
   - Do not rewrite the framework's detailed steps in this methodology.
   - Treat the framework as the process layer and this methodology as the ERP knowledge layer.

6. Carry ERP-specific context through the workflow.
   - Designs and plans should name affected module terms, tables, contracts, flows, rights, statuses, runtime assumptions, and documentation updates.
   - Implementation should update contracts or usage pages when public behavior or important module rules change.
   - Verification should distinguish static checks, runtime checks, blocked-by-access gaps, and runtime-unverified assumptions.

7. Record the outcome.
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
- When cross-module work goes ahead (not for a plain question): a link from the consumer to the owner contract page, and, when the owner module was changed, a cross-module entry in the owner's `session_state.md` plus an updated consumer list and change history on the owner contract page.

## Example

A user asks: "Make budget access respect the parent unit."

The methodology does not prescribe every step of the design and implementation workflow. It first prepares the ERP context:

- active module: budgeting;
- module terms: budget unit, parent unit, access scope, user department;
- likely evidence: module concept, budget hierarchy table contracts, access helper contracts, access usage flow, open questions about runtime configuration;
- likely risks: rights, active periods, hierarchy depth, missing setup, runtime data;
- documentation impact: table contract or access usage flow may need refresh.

After that, Superpowers or an equivalent workflow should drive the task: clarify scope, write the design, plan the implementation, make the change, verify it, and finish the branch or task record. The ERP methodology remains responsible for making sure the workflow receives the right proprietary context and writes durable ERP knowledge back when behavior changes.

A later task runs in an approval module `Beta`. The user asks: "Do we already have rules for which budget rows a user may see?" The consumer's knowledge base has no link yet, and no module was named, so the agent resolves the budgeting module `Alpha` through the module registry, finds the access contract page in `Alpha`'s knowledge base, and reports: the rule lives in `Alpha`'s access class, but it has no public method for row filtering. Nothing in `Alpha` is changed, and nothing is recorded in `Beta` yet: this was a question. The user then says to reuse the rule in `Beta`'s report; only now does the agent record a link to the `Alpha` contract page in `Beta`'s usage page.

The user then commands: "Add that method in `Alpha` and use it here." The agent reads `Alpha`'s module instructions, adds the owner API on top of the existing helpers, and writes `Beta`'s adapter. In `Alpha`, it appends a session entry "cross-module change from `Beta`: public row-access methods added for approval filtering, requested by the user", ending with `Alpha`'s previous next action copied unchanged, and adds `Beta` to the contract page's consumers and change history. The next session in `Alpha` sees what changed and why, and still knows where its own work stopped.

## Failure Modes

- Rewriting a third-party workflow as if it were part of this methodology.
- Starting implementation before the active module and key business terms are mapped.
- Loading raw source evidence before checking curated module concepts, contracts, and flows.
- Treating static source review as runtime confirmation.
- Updating code while leaving changed table, class, or usage contracts stale.
- Recording task decisions only in chat history.
- Letting the workflow framework replace ERP understanding instead of using it to structure the work.
- Changing another module in response to a question, when only a command allows changes there.
- Searching every module's knowledge base or code instead of following the consumer links, the named module, and the module registry in order.
- Writing into the owner module under the consumer's rules instead of the owner's module instructions.
- Changing the owner module without a mark there, so its next session finds unexplained changes.
- Adding a cross-module entry to the owner's `session_state.md` without carrying over the owner's own next action, so the owner loses its restart point.
- Taking the owner rule into work and leaving no link in the consumer, so the next task repeats the search.
- Recording a link or any other trace in the consumer after a plain lookup question, so a passing question is mistaken for a dependency.

## Assumptions And Runtime Limits

- Superpowers is recommended because it is available in this workspace and already provides a disciplined task lifecycle.
- Another workflow can replace Superpowers if it enforces comparable intake, design, planning, implementation, verification, and completion gates.
- This methodology should name the integration boundary, not copy external workflow instructions.
- Proprietary ERP runtime behavior may still require real data, permissions, configuration, UI state, or environment access to verify.

## Related Notes

- `05-module-concept-and-language.md`: defines the business-language entry point for task work.
- `07-tables-as-contracts.md`: defines table contracts used during task scoping.
- `08-libraries-and-class-contracts.md`: defines behavior contracts used during task scoping, and the owner API that cross-module work builds.
- `09-usage-flows-and-patterns.md`: defines scenario pages that connect contracts into business behavior.
- `11-how-emergent-capabilities-work.md`: downstream section mapping this workflow's mechanisms to the capabilities they produce.
- `12-practical-workspace-template.md`: downstream section for deciding where resulting knowledge belongs in a starter workspace.
