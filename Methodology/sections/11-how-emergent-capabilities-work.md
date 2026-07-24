# How Emergent Capabilities Work


## Reader Outcome

After this section, the reader can:

- Map each capability named in `02-emergent-capabilities.md` to the specific mechanism that produces it.
- Explain why a flat, always-loaded memory pattern cannot reproduce these capabilities at the same scale.
- Use each mechanism deliberately: read session state fully to recover history, switch modules without losing context, create shared instruments other modules can find.

## Core Explanation

`02-emergent-capabilities.md` named seven capabilities and left the mechanism unexplained on purpose — the point of that section was to show what the reader gets, not how. Now that the knowledge system, workspace bootstrap, and agentic workflow sections have introduced the actual pieces (module registry, layered knowledge base, `session_state.md`, confidence labels, the disciplined task workflow), this section can name, for each capability, exactly which piece produces it.

Each capability below is explained the same way:

- **What it is** — restated in one line from `02-emergent-capabilities.md`.
- **How DCR produces it** — the specific mechanism and file chain responsible.
- **Why a flat memory pattern cannot** — the structural limitation in a flat, always-loaded memory pattern that prevents the same result. This section uses a flat, always-loaded memory-bank convention as a representative example of that whole family of approach — a common way to give an agent persistent memory, built around one fixed set of files (project brief, product context, system patterns, tech context, active context, progress) read in full at the start of every session, with no per-module partitioning, no confidence labels, and no stop marker.
- **How to use it deliberately** — one concrete action the reader can take.

### 1. Session Without Loss

**How DCR produces it:** `session_state.md` records the active module, the last action, what was verified, what remains open, and the next action, ending at a stop marker (`<!-- AGENT-SESSION-STOP -->`). On restart, the agent reads the file, stops at the marker, and continues from that point.

**Why a flat memory pattern cannot:** its `activeContext.md` and `progress.md` describe the current state, but carry no stop marker — there is no boundary between "the last thing that happened" and "everything before it." Nothing in the pattern tells the agent where today's context ends and history begins.

**How to use it deliberately:** update `session_state.md` at the end of every task, not just when convenient — the capability depends on the file being current, not on the mechanism doing this automatically.

### 2. Switching Costs Nothing

**How DCR produces it:** `session_state.md` is per-module, not global. Module A's file and Module B's file are separate documents; opening one never touches the other. Switching modules is therefore just resolving a different active module through the module registry and reading a different file — there is nothing to blend.

**Why a flat memory pattern cannot:** the pattern has no per-module partitioning at all — `activeContext.md` describes whatever the whole project is doing, so working on two active areas at once means either the file describes both at once, or one area's notes overwrite the other's.

**How to use it deliberately:** keep every module's `session_state.md` genuinely separate — never let one module's restart notes reference or depend on another module's file being open at the same time.

### 3. Full Module History

**How DCR produces it:** `session_state.md` is append-only. Every session's entry is preserved above the stop marker of the entry that follows it. Reconstructing a module's history means reading the file from its first entry, not just the latest one.

**Why a flat memory pattern cannot:** `progress.md` and `activeContext.md` are overwritten each session by design — there is no append-only log of what happened, so past state is simply gone once the next session starts.

**How to use it deliberately:** to recover full history, read `session_state.md` from the beginning, not just the entry above the stop marker — that marker only marks where the *latest* session ended, not where useful history stops.

### 4. Remember Everything

**How DCR produces it:** knowledge lives at exactly one of two roots — `knowledge-base/modules/<module>/` for module-local facts, `knowledge-base/shared/` for facts that apply everywhere. Both roots are reachable through the same module-registry entry point in the same agent session, so there is no separate retrieval step for "shared" versus "local."

**Why a flat memory pattern cannot:** the pattern has one flat set of files with no shared/local distinction at all — everything is either in the six files or it isn't, so there is no structural way to scope a fact to "this module only" without it leaking into every session regardless of relevance.

**How to use it deliberately:** when creating something reusable, place it in `knowledge-base/shared/` deliberately rather than leaving it in one module's pages — the reachability is structural, but *which* root something lives in is still a human decision.

### 5. Find and Use the Best

**How DCR produces it:** each module's knowledge base has its own `INDEX.md` entry point. Referencing another module means resolving that module through the registry, opening its `INDEX.md`, and following the link to the relevant page — a routing operation, not a search. This is the mechanism that makes the capability possible at all: **it is the module registry and `INDEX.md` routing chain that produces fast cross-module reference, not the confidence labels.** Confidence labels play a supporting role once a page is found: a label tells the agent whether the found page's claims can be applied as-is or are worth checking further before reuse — that is what makes reuse *fast*, not what makes reuse *possible*.

**Why a flat memory pattern cannot:** the pattern has no module boundaries to route between — comparing "how module X handles this" against "how module Y handles this" is meaningless when there is only one undivided memory set describing everything at once. Reuse in that pattern means re-reading raw source in each project, because there is no per-module page to route to.

**How to use it deliberately:** say plainly which modules to compare — "look at how module X and module Y both handle this, and recommend the stronger approach" — the agent needs the registry to resolve both modules before it can compare their `INDEX.md` pages.

### 6. Agent Knows What's Checked

**How DCR produces it:** every important knowledge-base claim carries one of four labels — `confirmed`, `inferred`, `runtime-unverified`, `blocked-by-access`. Nothing enforces that a labeled claim is *correct*; what the label enforces is that the agent's own next action depends on which label is present, not on how confident the prose sounds.

**Why a flat memory pattern cannot:** the pattern has no label vocabulary at all — every sentence in its six files carries the same implicit weight, so the agent has no signal to distinguish a verified fact from an assumption baked into the prose.

**How to use it deliberately:** label a claim honestly at the moment you write it, not after the fact — an unlabeled claim defaults to being read as unverified, so the discipline only works if labeling happens during curation, not as cleanup.

### 7. Set the Task in Business Words

**How DCR produces it:** the module concept (`05-module-concept-and-language.md`) maps business vocabulary to technical objects ahead of time — terms, synonyms, primary entities, and extension points, each linked to the wiki, contract, or table page that carries the technical detail. When a request arrives in business language, the agent resolves it through that map first, then follows the links to the specific pages and source locations the request actually touches — including objects the request never named, when the module concept records that they share the same underlying rule.

**Why a flat memory pattern cannot:** the pattern has no structured business-to-technical map at that grain — whether the task is a fix, a feature, or a question, an entity or rule scattered across multiple unrelated-looking objects is only findable by reading or grepping raw source, so either the requester already has to know every location and name it, or the agent has to search broadly and hope it finds all of them.

**How to use it deliberately:** keep the module concept's terminology dictionary and extension points current as they're discovered, not just at bootstrap — a term the module concept doesn't yet map still forces the requester to supply the technical map themselves inside the request, the same as having no module concept at all.

## How These Capabilities Relate

- **Remember Everything** (single-window reachability across shared and local scope) is the precondition for **Find and Use the Best** — a workspace where local and shared knowledge are not both reachable from one window cannot support cross-module reuse at all.
- **Session Without Loss** and **Switching Costs Nothing** share one mechanism — the per-module, stop-marked `session_state.md` — applied along two different axes: how long you were away, and how many other modules you touched in between.
- **Full Module History** is the same file read a different way: from the first entry instead of from the stop marker.
- **Agent Knows What's Checked** does not produce **Find and Use the Best** — the module registry and `INDEX.md` routing chain does. What confidence labels contribute is trust: they are what lets the agent apply a pattern found in another module without re-verifying every claim on that module's page first.
- **Find and Use the Best** and **Set the Task in Business Words** both route, but in different directions. Find and Use the Best routes *between* modules to compare how each solves the same problem, via `INDEX.md`. Set the Task in Business Words routes *within* one module, from a single business sentence to the specific technical objects it touches, via the module concept's vocabulary map — a different mechanism producing a different kind of reach.

Adopting a subset of these mechanisms still produces the matching subset of capabilities. The full value appears once all of them are built and kept current together.

## Reproducible Procedure

1. For each capability you want from `02-emergent-capabilities.md`, find its matching subsection above and confirm the mechanism it names is actually built in your workspace — not just described in a plan.
2. If a capability is missing, check the specific file or convention responsible: no session continuity → check for a per-module `session_state.md` with a stop marker; no cross-module reuse → check that both modules have a populated knowledge base with an `INDEX.md`; confident-sounding but unverifiable answers → check whether claims actually carry confidence labels.
3. Do not assume a capability is "on" because the workspace template was copied once — a template gives you the empty structure; the capability appears only once the structure is populated and kept current.
4. When two capabilities appear related, check "How These Capabilities Relate" above before assuming one produces the other — the mapping is not always the obvious one, and getting it wrong (as an earlier draft of this section did, attributing cross-module reference to confidence labels instead of routing) misleads the next person who tries to fix a missing capability by touching the wrong mechanism.

## Required Artifacts

- A module registry that resolves the active module and can resolve any other module by name.
- A per-module `session_state.md` with an explicit stop marker.
- `knowledge-base/modules/<module>/INDEX.md` and `knowledge-base/shared/INDEX.md` as entry points.
- Confidence labels attached to claims at the time they are written, not retrofitted later.
- A populated module concept page for the active module, with business vocabulary mapped to technical objects (`05-module-concept-and-language.md`).

## Example

Continuing the worked example from `02-emergent-capabilities.md`: the user asks the agent to compare evidence-checking approaches across projects A, B, and C. The agent resolves all three through the module registry, opens each project's `INDEX.md`, follows the link to the evidence-checking page in each, and compares the three pages — no raw source read in any of the three. The recommendation it returns cites project B's page as `confirmed` (tested against real output) versus project C's page marked `inferred` (a documented but not independently verified approach) — the label is what lets the user trust the recommendation without re-checking project C's page personally before deciding.

## Failure Modes

- Reading only the latest `session_state.md` entry and concluding the module has no earlier history — the stop marker marks the latest session's boundary, not the start of useful history.
- Creating shared knowledge without confidence labels — unlabeled shared knowledge is indistinguishable from an unverified guess once another module starts relying on it.
- Expecting cross-module reference to work before the target module has a populated knowledge base — the agent can only route to a page that exists.
- Attributing a capability to the wrong mechanism, as with cross-module reference and confidence labels above — this doesn't just cause a wording mistake, it sends the next troubleshooting effort to the wrong file.
- Treating the workspace template as a one-time setup step instead of a structure that has to stay populated and current to keep producing these capabilities.
- Expecting Set the Task in Business Words from a module whose concept page exists but has an empty terminology dictionary or extension-point list — the mapping depends on that content being filled in, not on the page existing.
- Assuming Set the Task in Business Words only applies to bug reports — the module concept resolves any task shape (fix, feature, question) the same way, as long as the request's vocabulary is already mapped; a term outside the map still needs `06-knowledge-acquisition.md` first.

## Assumptions And Runtime Limits

- These mechanisms assume a model capable of following the workspace's own routing instructions and holding a working set of pages in context at once. On a small or low-cost model with a narrow context window, expect degraded results.
- No rotation or archival strategy is described yet for a `session_state.md` that has accumulated years of entries in one module — Full Module History assumes the file stays cheap to read from the start, which is untested at that scale.
- The comparisons behind these mechanism descriptions (`Evidence/01`, `Evidence/02`) are self-run, single-trial, single-model case studies, not peer-reviewed or independently replicated results.

## Related Notes

- `02-emergent-capabilities.md`: names the capabilities this section maps to mechanisms.
- `03-knowledge-system.md`: defines the memory layers and context-routing mechanisms used above.
- `05-module-concept-and-language.md`: defines the module concept mechanism behind Set the Task in Business Words.
- `04-workspace-bootstrap.md`: creates the concrete files (`session_state.md`, module registry, knowledge-base roots) this section assumes exist.
- `12-practical-workspace-template.md`: downstream section for turning these mechanisms into a practical starter workspace.
- `Evidence/01-hermes-agent-cross-framework-validation.md`: source for the session-state and confidence-label mechanism tests referenced above.
- `Evidence/02-context-mechanism-vs-flat-memory-pattern.md`: source for the routing and overread mechanism tests referenced above.
