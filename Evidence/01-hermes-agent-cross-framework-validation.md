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
session 1 left off. Second, the obvious objection to needing a dedicated
state file at all — "couldn't the agent just full-text-search its past
conversations instead?" — doesn't hold up under the author's own analysis
of that alternative: search doesn't know which past session is relevant
without a hint the agent doesn't have, it returns unstructured dialogue
instead of a structured state, and it has no stop marker — an agent using
it risks reading stale, superseded instructions along with the current
ones. The stop marker used is a literal `<!-- AGENT-SESSION-STOP -->`
line: the agent reads only the entry above it and treats everything below
as history, not current instruction.

**Limitations:** this simulates a lost session (clean context); it doesn't
test partial context retention, conflicting state (file says one thing,
workspace another), or a multi-module workspace where the agent must first
determine which module was active. The case against full-text session
search as a substitute, above, is reasoned analysis, not a fourth tested
condition — the agent without `session_state.md` was never actually
instructed to try searching past sessions as a recovery strategy in this
experiment.

## Test 4: Local artifact retrieval and its boundary (open-ended research)

**Hypothesis:** the routing advantage seen in Test 1 is specific to queries
whose answer already exists as a curated artifact somewhere in the
workspace. It should not appear — and DCR's extra structure should become
pure overhead — on queries that have no local artifact to route to.

**Method:** four follow-up rounds, run after Tests 1–3, against two
additional real workspaces set up the same way as Workspace A/B —
**Workspace C**, a product-engineering project with an internal knowledge
base of architecture and design-decision pages, and **Workspace D**, a
brand/content-strategy project with concept, research, and planning pages
— plus the methodology's own treatise. All four rounds used the same
backend model, `deepseek-v4-flash:cloud`, through Hermes Agent, and were
measured via the agent's own verbose logging — prompt-token totals from
its per-request usage summary, and `read_file` / `search_files` /
`browser_navigate` call counts — rather than the manual file-count method
used in Test 1. `read_file` and `search_files` are different operations
(reading one file in full vs. a content search across many) with
different costs; the tables below report them combined as one call count
per side for brevity, not as equivalent operations. Prompts varied across rounds between English and Russian;
within each round both variants still received the identical prompt. Two
of the four rounds also computed a skills-overhead-adjusted token figure
(subtracting a constant measured via a control prompt, to isolate the cost
of everything after the agent's own skill-loading); that adjustment
produces larger percentage swings on the cheaper local-retrieval tasks
below, but raw prompt-token totals — the number every round reported — are
used throughout here as the metric consistently available across all
four.

The first of the four rounds reused profiles carrying real prior session
history, and the agent's session-search tool could surface earlier answers
regardless of which structure was in front of it. Token counts from that
round are shown below for completeness but excluded from the comparison
claims; its transcripts are discussed separately, qualitatively, after the
token results. The later three rounds used clean, isolated profiles and
prompts not asked before, closing that leak.

**Local artifact retrieval — full results (two clean rounds, five
tasks):**

| Task | Baseline tokens | DCR tokens | Δ | Duration (B / D) | `read_file`+`search_files` calls (B / D) | Target found (B / D) |
| --- | :-: | :-: | :-: | :-: | :-: | :-: |
| 1 — single metrics page | 38,136 | 28,604 | **−25.0%** | 69s / 27s | 6+14 / 4+7 | yes / yes |
| 2 — single strategy page | 21,333 | 35,238 | +65.2% | 31s / 52s | 3+3 / 17+6 | no / yes |
| 3 — single competitor-analysis page | 60,599 | 31,700 | **−47.7%** | 127s / 32s | 17+12 / 3+2 | no / yes |
| 4 — four-page cluster on one topic | 33,790 | 30,484 | **−9.8%** | 41.9s / 30.0s | 7+4 / 8+3 | 1 of 4 pages / 4 of 4 pages |
| 5 — positioning question (qualitative; no token measurement taken) | — | — | — | 23.6s / 43.2s | 12 files / 14 files | full, but with unrelated overread and a shallower competitor angle / full, no overread, plus 2 extra sources baseline missed |

Task 2 is the one row where DCR used *more* tokens (+65%) and still counts
as the win: baseline's lower number is the cost of not finding the page —
it answered from a summary document instead of the dedicated one, and
reported five content strategies where DCR's answer, read from the actual
page, had six. Token cost only tells the right story once "did it find the
thing" is checked first, which is why both columns are reported together
here rather than tokens alone. Task 2 is also DCR's most call-heavy row
(17 `read_file` calls) — the source report attributes this to actually
walking the full routing chain rather than jumping straight to one page;
finding the right artifact doesn't always mean finding it in a single
hop.

**Pure web research, no local artifact relevant — full results (one
round, three tasks):**

| Task | Baseline tokens | DCR tokens | Δ | Duration (B / D) | `browser_navigate` calls (B / D) | Note |
| --- | :-: | :-: | :-: | :-: | :-: | --- |
| Market-size lookup | 92,545 | 101,278 | +9.4% | 517s / 900s | 137 / 26 | DCR paid for its 7-file routing-chain walk (entry points, not content pages) before concluding there was nothing local to route to, then did the same web research baseline did |
| Competitor list | 62,355 | 34,077 | **−45.4%** | 600s (timeout) / 82s | 36 / 5 | DCR delegated to parallel subagents; baseline hit its timeout with no complete answer |
| Trend summary | 51,879 | 73,785 | +42.2% | 58s / 232s | 8 / 16 | DCR did more browser navigation, not less |

**Contaminated round — token counts shown for completeness, not used as
evidence (one round, three tasks):**

| Task | Baseline tokens | DCR tokens | Δ | Note |
| --- | :-: | :-: | :-: | --- |
| Product description | 42,879 | 24,302 | −43.3% | baseline reproduced a stale, pre-correction description; DCR's curated page had the corrected version (discussed below) |
| Methodology principles | 31,694 | 29,612 | −6.6% | both found it; DCR's answer enumerated more principles in more depth |
| Market research | 98,721 | 142,103 | +44.0% | neither answer addressed the prompt's specific angle — not a clean comparison either way |

**Key finding:** the pattern holds on every local-retrieval task and
inverts on every web-only task. When the object of a query already exists
as an artifact in the workspace, DCR located it in every one of the five
tasks tested here — five for five, including all four pages of a
four-page cluster where baseline found only one. Where both sides answered
the same question, DCR was also the cheaper path: identically on task 1
(−25.0%, matching answers) and, more strikingly, on task 4 (−9.8%), where
it was simultaneously cheaper *and* four times more complete than baseline
(all 4 target pages vs. 1). Baseline's linear search degrades once a workspace
has enough files that the answer isn't the first thing found; in one case
(task 3) it read or searched 29 files hunting for a page it never located,
then answered from adjacent, less specific material instead. When no such
artifact exists, the same structure has nothing to route to: DCR still
paid the fixed cost of walking its routing-chain entry points before
concluding nothing local applied, then still had to do the same web
research baseline did, at a token cost baseline didn't pay — losing the
token comparison on two of the three purely-external tasks. The one
web-only task DCR won, it won for an unrelated reason — access to parallel
subagents, not the routing chain this document otherwise tests.

**On the contaminated round:** its token numbers are shown above for
transparency but not used as comparison evidence — five of its six runs
were flagged contaminated. One exchange from it is still worth reporting
on content alone. Both variants were asked to describe the same product.
Contamination should, if anything, have helped the uncurated baseline —
its session-search tool had access to the same prior sessions DCR's
routing chain did not need. Instead baseline reproduced a stale
description the project had already moved past after an earlier internal
correction; DCR's curated page carried the corrected version, which is why
its token count is lower here too (−43.3%) despite the contamination that,
on paper, should have narrowed the gap. A second task in that round
(methodology principles) also went to DCR, with a deeper answer. The third
task (open-ended market research) produced no usable comparison either
way — neither variant's answer addressed the specific angle the prompt
asked about, so baseline's lower token count on that task reflects a
shared miss, not an advantage for either side.

**Limitations:** single backend model, single run per task, across all
four rounds. One author designed, ran, and judged every round, including
the post-hoc, non-blinded reading of the contaminated round's transcripts
described above. Token accounting wasn't fully standardized across
rounds — two of the four also computed the skills-overhead-adjusted figure
mentioned in Method, not shown in the tables, which would inflate the
local-retrieval percentages further; raw prompt-token totals were used
throughout instead as the metric available in all four. The web-only win
attributed to subagent delegation is a capability of the agent product,
not of the routing mechanism this document otherwise tests, and should
not be read as a second, independent way DCR helps. And the corrected
artifact that let DCR beat a stale answer in the contaminated round only
existed because a curator had already revised it after that same error
was caught in earlier testing — the ongoing curation cost Test 1 already
flags, not a one-time setup cost.

## What this does and doesn't show

Across all four tests, the same underlying structure produced large,
consistent effects on a second agent product, in a domain with no code, no
ERP, and no compiler or runtime signal to fall back on: a linked graph of
knowledge-base pages, kept navigable by stop markers, confidence labels,
and conditional-reading rules, and built in the first place by a
documentation curator turning raw evidence into cross-referenced pages.
That's the strongest available evidence so far that this graph-and-rules
structure is doing the work, not something specific to any one agent
product or to ERP data shapes. Test 4 also draws the boundary: the same
structure adds token overhead with no compensating benefit on open-ended
web research, where there is no local artifact to route to — the advantage
documented here is specific to retrieving something that already exists in
the workspace, not a general claim about agent performance.

It does not show independent, third-party validation: one author designed,
ran, and wrote up all four tests, once each, on their own workspaces.
Treat the numbers above as a well-documented case study, not a
peer-reviewed result.
