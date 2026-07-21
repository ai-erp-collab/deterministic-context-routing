# Navigation Discipline vs. a Flat Memory Pattern: Deterministic Context Routing Compared to the Cline Memory Bank Pattern

**Status:** self-run test, single trial per task, one model, not peer-reviewed.
See the Limitations note at the end.

## What this is

In July 2026, this methodology's author ran a controlled comparison between
two context mechanisms on the same three real internal services, same
runtime, same model: this methodology's Deterministic Context Routing (DCR)
workspace, and the Cline Memory Bank pattern (a flat set of always-loaded
memory files, ported as a comparable mechanism — no module registry, no
layered knowledge base, no confidence labels).

**This is not an independent third-party evaluation.** It was designed,
run, and scored by the methodology's own author. Real service names,
internal identifiers, and the specifics of each service's anti-hallucination
implementation are not reproduced here — only the category of mechanism
each uses (see Task battery below) — because the underlying services are
real, proprietary, in-production systems.

**One exclusion rule, stated up front:** two of the six tasks (Task 2 and
Task 4, both against Service Beta) had a first attempt where the DCR agent
skipped its own onboarding procedure entirely — it went straight to source
search instead of reading the module registry and knowledge base at all.
That is a failure to follow the mechanism's own protocol, not a result about
the mechanism — it is the same thing as scoring a workspace convention that
was never actually applied. Both tasks were re-run once, in a fresh session,
with the identical prompt; the re-run figures are what appear in the tables
below. The original, protocol-skipping attempts are not used anywhere in
this document's scoring.

## Test environment

Three real internal services (renamed Service Alpha, Service Beta, Service
Gamma), same model (a lower-tier Claude model, held constant across every
task and every arm), same six task prompts run once per arm:

- **Alpha-mechanism** — this methodology's workspace: module registry,
  layered knowledge base (concept / contracts / usage / tables pages),
  confidence labels, session state with a stop marker.
- **Beta-mechanism** — the Cline Memory Bank pattern: a fixed set of six
  files (project brief, product context, system patterns, tech context,
  active context, progress) with one binding rule — read all six, in full,
  at the start of every session, regardless of what the session is about.
  No per-module partitioning exists in the pattern itself.

Both mechanisms were built from the same underlying service documentation,
so the comparison is about *routing and selection*, not about which mechanism
had better source material.

## Task battery

Six tasks against the same three services: two cold-start (asking the agent
to extend an existing pattern in one service), two repeat-topic (asking the
same thing again in a later session, testing whether the mechanism itself
carries the answer or the agent has to re-derive it from source), and two
cross-module (spanning two of the three services at once — one asking about
a deployment integration, one asking the agent to compare how the two
services each defend against LLM hallucination and recommend which approach
a hypothetical third service should reuse).

## Results

### Completeness (rubric-scored, 0–1 per task)

| Task | Type | Alpha-mechanism | Beta-mechanism |
| --- | --- | :-: | :-: |
| 1 | cold-start | 1.00 | 1.00 |
| 2 | cold-start | 0.80 | 0.80 |
| 3 | repeat-topic | 0.67 | 1.00 |
| 4 | repeat-topic | 1.00 | 1.00 |
| 5 | cross-module | 1.00* | 0.60 |
| 6 | cross-module | 0.80 | 0.60 |
| **Average** | | **0.88** | **0.83** |

\* Task 5's rubric penalized correctly identifying two deploy scripts as
deprecated (the rubric assumed they were still the expected pattern). That
assumption was independently checked against the actual, currently-operative
deploy path in a separate session before this document was written, and
confirmed wrong — the scripts really are unused. Both mechanisms had access
to this project's real deploy history; Alpha-mechanism's answer flagged the
deprecation correctly, Beta-mechanism's did not. Scored as a legitimate
rubric correction, not a cherry-picked one — no equivalent correction was
applied anywhere Alpha-mechanism was simply wrong (see Task 2 in Limitations).

### Navigation discipline: overread and re-discovery

These two numbers matter more than the completeness average above, because
they measure whether the mechanism itself was actually used, not just
whether the final answer happened to be right.

**Overread** — did the agent read raw source files when the task's own
necessary-file set says it shouldn't have needed to:

| | Alpha-mechanism | Beta-mechanism |
| --- | :-: | :-: |
| Tasks overread (of 4 applicable) | 0/4 | 3/4 |

**Re-discovery** — on the two repeat-topic tasks, did the mechanism answer
from its own recall, or did the agent re-derive the answer from raw source
(a miss, since the whole point of a persistent mechanism is not having to
re-derive):

| | Alpha-mechanism | Beta-mechanism |
| --- | :-: | :-: |
| Tasks re-derived from source (of 2 repeat-topic) | 0/2 | 1/2 |

**What this looks like in practice:** on the two cross-module tasks,
Beta-mechanism read six-plus raw source files per task even though its own
six memory files were sitting right there — the flat, always-loaded pattern
doesn't stop an agent from also going straight to source, it just adds cost
on top. Alpha-mechanism's cross-module answers came entirely from its
layered knowledge base, zero source files touched, on both tasks.

**Incidental correctness auditing:** twice, working an assigned task,
Alpha-mechanism surfaced a real defect nobody had asked it to look for —
once a stale, mislabeled claim in its own knowledge base (traced and
confirmed wrong by direct verification against the service's real
constraints), and once a documentation gap unrelated to the task at hand
(a broken cross-reference plus a section that was a leftover copy from a
different service's deploy docs). Neither mechanism was asked to audit
anything; Beta-mechanism's equivalent runs did not surface either issue.
This is a single occurrence each, not a measured rate — reported because it
speaks to what a disciplined, source-linked knowledge base does as a
byproduct of normal use, not because two events establish a pattern.

### Cost — a secondary result, not the headline

| | Alpha-mechanism | Beta-mechanism | Δ |
| --- | :-: | :-: | :-: |
| Total cost, 6 tasks | $1.43 | $2.03 | −30% |

This gap is not a separate advantage — it is the direct cost of the overread
and re-discovery measured above: Beta-mechanism paid for source reads that
Alpha-mechanism's routing made unnecessary. Real, and in the same direction
as everything above, but the size of this number is a property of the three
services chosen for this test — see the next section for why that matters
more than the percentage itself.

## Why small services, and what a larger project projects to

The three services in this test were deliberately small (combined raw
source in the tens of megabytes) so the comparison would be roughly fair to
Beta-mechanism. That choice understates Beta-mechanism's real weakness: its
six memory files must describe the *entire* project in one flat set,
because the pattern has no per-module partitioning — so their size scales
with total project size and complexity, while Alpha-mechanism's per-task
read stays roughly constant, because it only opens the module (and the
handful of knowledge-base pages) the task actually concerns.

To make that concrete without running a live test on a larger project, this
document estimates from a real reference project in the same workspace
ecosystem — a genuinely multi-module system, several times the scope of any
one of the three test services. Using the actual measured ratio between
this test's two mechanisms (Beta-mechanism's six files came out to roughly
half the size of Alpha-mechanism's full knowledge base), the same ratio
applied to that reference project's actual knowledge-base size projects to
roughly **60,000 tokens that a Beta-mechanism-style flat memory set would
require reading in full, on every single session, regardless of which
module the session concerns** — versus Alpha-mechanism's typical per-task
read, which stayed in the 5,000-6,000 token range in this test and would be
expected to stay in that range on the larger project too, since it opens
one module's slice, not the whole thing.

Sixty thousand tokens is roughly 30% of a smaller model's entire context
window, consumed before the agent has done any actual work — a cost that
compounds with project size for a flat mechanism and stays flat for a
routed one. This is a projection from measured ratios, not a second live
experiment, and is presented as exactly that.

## Limitations

- Six tasks, one run each per mechanism (n=1), a single model held constant
  — this measures one pair of mechanism snapshots on one day, not a
  distribution. A separate, frozen protocol with n=2 per cell across two
  models exists for a fuller version of this comparison; this document
  reports the smaller, exploratory battery only. The cross-module cell shows
  the widest gap (1.00/0.80 vs. 0.60/0.60) and rests on only one task each —
  it is the cell most in need of a higher n (n=3+) before the gap should be
  read as reliable rather than suggestive.
- Task 2's rubric item on whether a format change requires a database
  migration favors neither mechanism uniformly: in this test, Alpha-mechanism
  repeated an unverified claim from its own knowledge base rather than
  checking it against the service's actual constraint (which turned out to
  be looser than the claim states); in a separate run under the same
  conditions, Beta-mechanism checked and got it right. No completeness
  correction was applied here in Alpha-mechanism's favor — this is the
  counterpart to the Task 5 correction above, kept in for balance.
- Two tasks (Task 2, Task 4) are reported from a second attempt after the
  first attempt skipped the mechanism's own onboarding procedure — see the
  exclusion rule stated at the top of this document.
- The scaling projection is a ratio-based estimate from one reference
  project's real knowledge-base size, not a second live test — it should be
  read as an illustration of a structural difference (routed vs. flat
  reading), not as a measured result with its own error bars.
- Cost figures are for one lower-tier model on one day; absolute numbers
  will differ by model and will not reproduce exactly on a re-run.
