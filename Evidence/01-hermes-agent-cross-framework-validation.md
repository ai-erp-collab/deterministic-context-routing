# Cross-Framework Validation: Deterministic Context Routing via Hermes Agent

**Status:** self-run test, single trial, not peer-reviewed. See the
Limitations note at the end of each section and the closing summary.

## What this is

In July 2026, this methodology's author ran a set of controlled
comparisons using [Hermes Agent](https://github.com/NousResearch/hermes-agent),
an autonomous agent product built by Nous Research — a different agent
product from the ones this methodology is normally used with. Two of the
author's own real, non-ERP workspaces were duplicated into
a "flat" version (no Deterministic Context Routing structure) and a "DCR"
version (module registry, layered knowledge base, confidence labels,
session state with a stop marker), then given to isolated Hermes Agent
instances with identical prompts.

**This is not an independent third-party evaluation.** It was designed,
run, and written up by the methodology's own author, using a real
third-party agent product as the test instrument. Nothing here should be
read as an endorsement by Nous Research.

## Test environment

Two workspaces, both plain-text knowledge bases with zero executable
code — no compiler, no build step, no runtime checks available, the same
"no ground truth from tooling" condition this methodology deliberately
targets in ERP work, just without ERP's scale:

- **Workspace A** — a working project with drafts, templates, guidelines,
  and reference material, ~32 files.
- **Workspace B** — a working project with recorded decisions, concept
  notes, and research material, ~41 files.

Each workspace was set up twice: once with a flat `docs/wiki/`-style
structure, once with a DCR-structured `knowledge-base/` (shared vs.
module-specific layers), a `modules.md` registry, confidence-labeled
pages, and `session_state.md` with a stop marker. Two isolated agent
instances ran against identical file content, differing only in that
structure.

Structurally, the DCR version is a graph, not a flat file dump: the module
registry points into layered knowledge-base pages, each page links out to
source evidence or related pages, and `session_state.md` links back into
whichever pages recorded the durable facts. Stop markers, confidence
labels, and conditional-reading rules are the discipline that keeps an
agent traversing that graph efficiently — entering at the right node,
following only the edges the current task needs, and stopping before
stale or irrelevant material — rather than scanning it exhaustively. The
graph's edges don't appear on their own: building them (turning scattered
raw material into cross-referenced pages) is a separate curation step,
covered in Test 1's limitations below.

## Test 1: Context routing (information retrieval)

**Hypothesis:** an explicit routing chain (module registry → layered
knowledge base → stop markers) gets an agent to the right file directly,
instead of scanning linearly until it happens to find an answer.

**Method:** both agents received the same six information-retrieval
prompts against their respective workspace copy — a mix of real questions
about the workspace content and a few synthetic ones designed to probe
specific structural gaps (e.g. a question with no dedicated page in the
flat structure).

| Task | What was being looked up | Files read (flat) | Files read (DCR) |
| --- | --- | :-: | :-: |
| 1 | A house style rule | 3 | 1 |
| 2 | A product concept's description, stack, and architecture | 8 | 1 |
| 3 | External research citations mentioned in the workspace | 1 | 1 |
| 4 | A recorded policy decision | 5 | 1 |
| 5 | A backlog of planned items | 3 | 1 |
| 6 | A comparison document | 3 | 1 |

**Results:**

| Metric | Flat | DCR | Δ |
| --- | :-: | :-: | :-: |
| Total files read (6 tasks) | 23 | 6 | −74% |
| Avg files read per task | 3.8 | 1.0 | −74% |
| Tasks completed fully | 4/6 | 6/6 | +33% |
| Tasks with overread (read more than needed) | 3/6 | 0/6 | −100% |
| Tasks needing user clarification | 1/6 | 0/6 | −100% |

**Key finding:** the worst case (Task 2) had the flat agent piece an
answer together from 8 files scattered across two workspace-internal
projects, while the DCR agent went straight to one curated concept page.
On two synthetic tasks (5 and 6), the flat agent produced a partial
answer — the information existed but was fragmented across files it never
fully assembled; the DCR agent found a single page a documentation curator
had already assembled from the same underlying material.

**Limitations:** six tasks, one run each, no repeated trials — this
measures one pair of workspace snapshots, not a distribution. Three of the
six tasks were synthetic by design, built to probe specific structural
gaps — including fragmented information (Task 5) and a missing curated
page (Task 6) — that occur naturally in real workspaces, rather than
drawn from real historical requests. Part of the DCR agent's advantage on
Tasks 2, 5, and 6 came from
work done before either agent ran: a documentation curator had already
turned scattered raw material into a single cross-referenced page. That
curation step is itself part of the methodology, not something outside
it, but it means this test measures the graph-plus-curation system
together, not routing in isolation. Wall-clock time was also lower for the
DCR agent (49.2s vs. 54.9s) — a single measurement, not a controlled cost
benchmark, and not broken down by token count.

## Test 2: Confidence labels (truthfulness)

**Hypothesis:** requiring an agent to mark each claim's evidential status
(`confirmed`, `inferred`, `runtime-unverified`, `blocked-by-access`)
prevents it from stating unverified or planned information as settled
fact.

**Method:** two isolated agents received the exact same one-page
product-concept document and the same instruction — write a report on the
product, using only the supplied document. One copy of the document had
every claim written as plain prose; the other had every claim prefixed
with an explicit confidence label. The source document mixed genuinely
confirmed facts, one planned-but-unimplemented feature, and a couple of
capabilities that were described but never independently confirmed.

**Results:**

| Metric | Without labels | With labels |
| --- | :-: | :-: |
| Total claims in the report | 21 | 24 |
| Unqualified claims (stated as plain fact) | 21 (100%) | 0 (0%) |
| Labeled `confirmed` | — | 7 |
| Labeled `inferred` | — | 1 |
| Labeled `runtime-unverified` | — | 16 |
| Labeled `blocked-by-access` | — | 0 |

(`confirmed` — stated directly in the source; `inferred` — a reasonable
conclusion, not stated outright; `runtime-unverified` — plausible but not
confirmed by any given source; `blocked-by-access` — the source needed to
confirm it was unavailable.)

**Key finding:** without labels, the agent stated a planned, unimplemented
feature as a working part of the product — indistinguishable in the text
from the genuinely confirmed facts around it. With labels, the same claim
was correctly marked `inferred`. The labeled report also had three more
claims, not fewer — the act of labeling made the agent enumerate
confirmed/inferred/unverified claims separately instead of folding them
into one confident paragraph.

**Limitations:** tested on one document, one claim mix, one run per
condition. Not tested: labeling overhead on response length/cost, or how
the agent behaves when two labeled sources disagree.

## Test 3: Session state (continuity)

**Hypothesis:** a `session_state.md` file with an explicit stop marker
lets an agent resume exactly where a prior session left off, without
asking the user to re-explain what was already done.

**Method:** a two-session simulation. Session 1 (identical for both
agents): analyze a source document (a meeting transcript) and draft an
article structure from it, then finish. Session 2: a clean context (no
conversation history) receives only the prompt "continue the work on the
article." One agent's workspace carried a `session_state.md` with a stop
marker recording what session 1 had done; the other agent's workspace had
no such file.

**Results:** as expected, the agent without a state file had no way to
know what had already been done and had to ask the user; the agent with
one resumed immediately. That baseline is confirmed in the table below —
the part worth reading is the Key finding after it, which covers what it
actually took and what didn't work as a substitute.

| Question | Without session_state.md | With session_state.md |
| --- | :-: | :-: |
| Knows what was already done? | No | Yes |
| Recovery strategy | Ask the user for context | Read session_state.md, stop at the marker |
| First action in session 2 | States it has no context and asks the user to re-explain | Resumes at the recorded next action (drafting) |
| Risk of redoing session 1's work | 100% | 0% |

**Key finding:** two things don't show up in the table above. First, how
little state was needed: nine lines — module, goal/status, files touched,
key facts extracted, confidence-labeled assumptions, what was already
verified, and the next action — were sufficient to resume exactly where
session 1 left off. Second, the agent without a dedicated state file
wasn't actually out of options: a full-text search over past conversations
was available in the workspace and was considered, then rejected as a
substitute. It doesn't know which past session is relevant without a hint
the agent doesn't have, it returns unstructured dialogue instead of a
structured state, and it has no stop marker — an agent using it risks
reading stale, superseded instructions along with the current ones. The
workaround that looks like it should work doesn't. The stop marker used is
a literal `<!-- AGENT-SESSION-STOP -->` line: the agent reads only the
entry above it and treats everything below as history, not current
instruction.

**Limitations:** this simulates a lost session (clean context); it doesn't
test partial context retention, conflicting state (file says one thing,
workspace another), or a multi-module workspace where the agent must first
determine which module was active.

## What this does and doesn't show

Across all three tests, the same underlying structure produced large,
consistent effects on a second agent product, in a domain with no code, no
ERP, and no compiler or runtime signal to fall back on: a linked graph of
knowledge-base pages, kept navigable by stop markers, confidence labels,
and conditional-reading rules, and built in the first place by a
documentation curator turning raw evidence into cross-referenced pages.
That's the strongest available evidence so far that this graph-and-rules
structure is doing the work, not something specific to any one agent
product or to ERP data shapes.

It does not show independent, third-party validation: one author designed,
ran, and wrote up all three tests, once each, on their own workspaces.
Treat the numbers above as a well-documented case study, not a
peer-reviewed result.
