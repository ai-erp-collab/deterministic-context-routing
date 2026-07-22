# Knowledge System


## Reader Outcome

After this section, the reader can:

- Explain the memory layers used by the methodology.
- Decide which layer should hold a fact, rule, artifact, or restart note.
- Explain why the method manages context instead of loading all available data.
- Use context-routing patterns to avoid loading irrelevant memory.
- Use the rule "define before use" when writing methodology sections or agent instructions.

## Core Explanation

The previous section named the problem: the agent needs necessary and sufficient context, but the available evidence is too large and too uneven to load all at once. The knowledge system is the answer. It separates memory into layers with different lifetimes and purposes.

Start with the product structure. A proprietary ERP workspace represents an ERP project. The project contains global settings, shared platform conventions, reusable contracts, and multiple business modules. A module is a bounded business area inside the ERP project: budgeting, purchasing, approvals, payroll, inventory, or another domain slice. Global knowledge belongs to the project level. Local behavior belongs to the module level.

Modules can be large enough to become knowledge systems of their own. Budgeting, for example, may contain hierarchy rules, limits, documents, access behavior, formulas, reports, table contracts, and helper libraries. This is why the method separates shared context from module context, and why it does not ask the agent to load the whole project for every task.

The memory layers are:

- System memory: model behavior, training, platform defaults, and hidden runtime instructions. The project cannot edit this layer directly. The project compensates for it by writing explicit local rules, examples, and verification gates.
- Agent instruction memory: files or settings that tell the current agent how to work in this workspace. In this project the main file is `AGENTS.md`. In another environment it may be `CLAUDE.md`, `GEMINI.md`, workspace instructions, or another agent-specific rule file.
- Short memory: compact restart context for the current workspace or module. In this project it is `session_state.md`.
- Medium memory: task-specific designs, plans, review notes, open questions, and work-in-progress decisions.
- Long memory: curated wiki pages and knowledge-base pages that should remain useful across tasks.
- Project memory: ERP-level knowledge such as global settings, shared platform conventions, reusable contracts, and cross-module decisions.
- Module memory: local module knowledge such as module purpose, terms, boundaries, contracts, usage flows, tables, and decisions.
- Shared product memory: reusable product or platform knowledge that applies across modules.
- Source evidence: raw and processed artifacts, source examples, exported schemas, user documentation, and runtime observations that support claims but are not always cheap to read directly.

These layers are not ranked by importance. They are ranked by retrieval purpose. A session note is good for resuming tomorrow, but bad as the only home for a table contract. A raw export is good as evidence, but bad as the first thing an agent reads. A module wiki page is good for local behavior, but bad for ERP-level rules that should apply across all modules.

Short memory has two roles that should not be confused. The first role is restart memory: what changed, what was verified, what remains open, and what the next useful action is. The second role is a compact activity index: which module was active and which durable pages or artifacts changed recently. `session_state.md` can point toward durable knowledge, but it should not become the durable knowledge itself.

Source evidence also has a lifecycle. A raw artifact is not "done" when it is copied into the workspace. It becomes useful when it is recognized, parsed or inspected, connected to curated pages, and recorded in an artifact ledger. Later evidence can revise earlier curated pages. The knowledge system should therefore make revision normal: facts can move from uncertain to confirmed, from partial to superseded, or from local to shared when new evidence justifies the change.

The knowledge system must also prevent over-reading. A memory layer is useful only when the agent can enter it through a narrow route, stop before stale context, and follow links only when the current task needs them. This is deterministic context routing.

Deterministic context routing commonly follows this chain: `modules.md` resolves the active module, the module concept maps business language to technical anchors, wiki pages and contracts provide compact knowledge, artifact indexes point to evidence, and `session_state.md` records current restart context. The chain can branch, but it should always tell the agent where to enter, how far to read, and when to stop.

Context routing uses four mechanisms:

- Stop markers: explicit boundaries that tell the agent where to stop reading. A session-state entry, for example, ends at `<!-- AGENT-SESSION-STOP -->` so yesterday's history does not become today's instruction.
- Navigation links: indexes, related-notes sections, artifact ledgers, and wiki entry points that let the agent jump to the smallest relevant page instead of scanning a whole folder.
- Conditional reading instructions: rules such as "read this page when the task touches access rules" or "inspect source evidence only when curated memory is missing, stale, or insufficient."
- Summaries with deep links: short curated pages that state the useful fact and link to deeper evidence, so the active context carries the conclusion and not the entire source body.

These mechanisms are as important as the folders themselves. A wiki without indexes becomes a source dump. A session log without stop markers becomes stale context. A source root without curated entry points invites broad reading. The method therefore treats markers, links, aliases, and "read-if-needed" instructions as first-class documentation.

Documentation is therefore a working product, not cleanup. A page is useful when it routes future work: it names the claim, attaches a confidence label, links to evidence, and tells the agent whether deeper reading or runtime verification is needed.

The pattern is general: define a memory layer, define its entry points, define its stop conditions, and define when to descend into deeper evidence. Later sections reuse pieces of this pattern. Workspace bootstrap creates the files and markers. Module concepts provide business-language entry points. Knowledge acquisition explains when to move from curated memory into source evidence. Task intake uses conditional reading to keep implementation context small.

The writing rule follows from the same model: define before use. If a section asks the reader to create `AGENTS.md`, the reader must already know what an agent instruction file is for. If a section mentions module memory, it must first explain module memory. This keeps the methodology itself aligned with the context-management principle it teaches.

## Reproducible Procedure

1. Identify the fact or artifact being handled.
   - Is it an instruction, restart note, task decision, durable contract, shared pattern, module rule, or source evidence?

2. Place it in the smallest correct memory layer.
   - Agent behavior rule: agent instruction memory.
   - Current restart context: short memory.
   - Task reasoning: medium memory.
   - Reusable curated fact: long memory.
   - ERP-level or cross-module fact: project memory or shared product memory.
   - Module-specific fact: module memory.
   - Original export or source observation: source evidence.

3. Record `session_state.md` as a pointer, not as the final home for durable facts.
   - Keep restart notes compact: current work, decisions, verification, next action.
   - Use them as an activity index to find recently touched modules, pages, or artifacts.
   - Move reusable facts into module or shared memory before they are needed again.

4. Prefer curated entry points over raw evidence during task intake.
   - Search module memory first when the task names a module.
   - Search shared memory for reusable platform behavior.
   - Inspect source evidence only when curated memory is missing, stale, or insufficient.

5. Keep the active context bounded.
   - Load the smallest page, source range, artifact summary, or section needed.
   - Avoid broad source dumps unless the task is explicitly knowledge acquisition.
   - Record links to deeper evidence instead of pasting large bodies into active notes.

6. Add context-routing controls.
   - Put stop markers on logs or state files that accumulate history.
   - Add `INDEX.md`, related notes, aliases, and artifact ledgers for long-memory areas.
   - Write conditional reading instructions where broad reading would be tempting.
   - Prefer summaries with deep links over copied source bodies.

7. Maintain evidence revision.
   - Keep raw artifacts auditable until they are recognized and connected.
   - Move artifacts to processed only after related curated pages are created or refreshed.
   - Revise wiki pages when new evidence confirms, narrows, or contradicts prior interpretation.
   - Record superseded or runtime-unverified claims explicitly.

8. Mark uncertainty at the same layer where the claim is stored.
   - A wiki page can be `partial`.
   - A claim can be `confirmed`, `inferred`, `runtime-unverified`, or `blocked-by-access`.
   - A plan can list runtime assumptions.
   - A session note can say verification is pending.
   - A known issue can define required handling for recurring risk.

9. Update discoverability.
   - Add or update `INDEX.md` files for wiki pages.
   - Add aliases for terms users naturally type.
   - Keep session state short so it stays useful as short memory.

## Required Artifacts

- Agent instruction file, for example `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or another environment-specific rule file.
- Short-memory file, for example root or module `session_state.md`.
- Medium-memory folders for designs, plans, and review notes.
- Long-memory wiki or knowledge-base roots.
- Shared product memory root.
- Module memory root.
- Source evidence folders for raw and processed artifacts.
- Index pages that make long-memory pages discoverable.
- Stop markers for append-only or history-like files.
- Conditional reading instructions for expensive evidence or optional context.
- Related-notes links and artifact ledgers that route from summaries to deeper evidence.
- Revision notes on curated pages or artifact ledgers when new evidence changes earlier knowledge.
- Confidence labels on important claims, using `confirmed`, `inferred`, `runtime-unverified`, or `blocked-by-access`.

## Example

In the Methodology module, the request "continue work on the methodology" should not load every source document. The useful context is layered:

- short memory: latest `Methodology/session_state.md` entry;
- module memory: `Methodology/Wiki/section-map.md`, `insights.md`, `decisions.md`, and open questions;
- long source material: selected `docs/methodology/*` drafts;
- agent instruction memory: root and module `AGENTS.md`;
- source evidence: existing project/module wiki and workspace rules when a claim must be grounded.

The active context becomes small enough to write the next section, but still grounded in the project.

The same request also demonstrates context routing. The agent reads the current module session only until `<!-- AGENT-SESSION-STOP -->`, enters the wiki through section maps and insights, follows related notes only when the next section needs them, and leaves older source drafts outside the active context unless a claim needs grounding. The important behavior is not that the evidence exists. The important behavior is that the workspace tells the agent how far to read.

## Failure Modes

- Treating every file as equal context: the agent reads too much and loses the task boundary.
- Creating memory without routing controls: useful facts exist but the agent must scan too much to find them.
- Writing documentation as cleanup: pages describe work after the fact but do not route the next agent to the right context.
- Omitting stop markers: old history leaks into current task context.
- Omitting navigation links: the agent enters folders instead of specific pages.
- Writing unconditional "read everything" instructions: optional background becomes mandatory noise.
- Treating session state as long memory: durable facts disappear into restart notes.
- Treating raw artifacts as wiki: source evidence exists but remains too expensive to use.
- Putting shared rules in module memory: other modules rediscover them.
- Putting module-specific behavior in shared memory: local behavior becomes overgeneralized.
- Writing instructions before defining their referenced entities: the reader follows file names without understanding their purpose.
- Depending on system memory: the project assumes the agent knows platform internals it does not know.

## Assumptions And Runtime Limits

- The project cannot directly rewrite the agent's system memory.
- The project can compensate with local instruction files, curated examples, and verification rules.
- Some source evidence may be incomplete or static-only.
- The method is successful when the agent receives the smallest context that can safely support the task.

## Related Notes

- `01-why-this-method-exists.md`: defines the context-management problem.
- `04-workspace-bootstrap.md`: turns this memory model into concrete files and folders.
- `05-module-concept-and-language.md`: explains module memory as the language bridge for task intake.
- `12-practical-workspace-template.md`: downstream section for turning the memory model into a practical starter workspace.
- `Methodology/Wiki/insights.md`: records the necessary-and-sufficient context principle.
