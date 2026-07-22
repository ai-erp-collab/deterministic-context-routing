# Deterministic Context Routing™

![License: BSL 1.1](https://img.shields.io/badge/license-BSL%201.1-blue)
![Status: v0.4.0-draft](https://img.shields.io/badge/status-v0.4.0--draft-orange)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)

🇬🇧 English (this page) | [🇺🇦 Українська](uk/README.md)

> Documentation is routing infrastructure, not cleanup prose.

A methodology for giving AI agents necessary-and-sufficient context in any
large, under-documented codebase — without flooding them with raw source
dumps, and without losing continuity between sessions. Proven on the
hardest compounding case: large, proprietary ERP systems with no compiler
and no git.

## Contents

- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [What You Get](#what-you-get)
- [Why ERP](#why-erp)
- [Who This Is For](#who-this-is-for)
- [Quickstart](#quickstart)
- [How This Compares](#how-this-compares)
- [In Good Company](#in-good-company)
- [Grounded In](#grounded-in)
- [License](#license)
- [Contributing](#contributing)

## The Problem

- Proprietary, large ERP systems hide the real complexity in table
  conventions, business vocabulary, and historical decisions — not in the
  code itself.
- Agents either get flooded with raw source dumps or get too little
  context, and start inventing behavior that was never there.
  [[1]](#grounded-in)
- Long-lived work loses continuity between sessions when the only memory
  is chat history. [[2]](#grounded-in)
- Runtime and compiled verification are often unavailable in closed,
  proprietary environments, so uncertainty has to be tracked explicitly
  instead of assumed away. [[3]](#grounded-in)
- Documentation efforts stall because they're treated as cleanup work after
  the "real" work is done, so they never actually happen.

## The Solution

- **Deterministic Context Routing** — a fixed path from a request to
  exactly the context it needs: module registry -> module concept ->
  wiki/contracts -> artifact index -> session state.
- **Curated Knowledge Base** — raw evidence (table exports, source
  examples, runtime observations) is turned into compact, cross-referenced
  pages before an agent needs them, so routing has something correct and
  current to find instead of a source dump to search.
- **Confidence Labels** — every important claim is tagged `confirmed`,
  `inferred`, `runtime-unverified`, or `blocked-by-access`, so agents and
  humans both know what has actually been checked.
- **Session State ≠ Git** — `session_state.md` carries intent, evidence,
  assumptions, and next action: information Git history was never designed
  to hold, and which stays necessary even in projects with full Git, CI,
  and test access.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/context-routing-diagram-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/context-routing-diagram-light.svg">
  <img alt="Deterministic Context Routing, three connected panels: Deterministic Routing (User Task Intake resolved through the Module Registry in modules.md to a Module Concept Page); Layered Memory System (Short Memory in session_state.md, Medium Memory in docs/, Long Memory holding Tables as Contracts, Class Contracts, and Usage Flows and Patterns, and Source Evidence moving Raw to Curated to Processed); Agent Engine and Gates (Superpowers workflow integration, a Bounded Active Context, a Confidence Matrix of confirmed, inferred, runtime-unverified, and blocked-by-access, and Static Verification Gates); a Continuous Documentation Sync loop feeds discoveries from the Agent Engine back into routing and memory" src="assets/context-routing-diagram-light.svg">
</picture>

## What You Get

These aren't features you configure — they emerge once the workspace structure above is in place.

- **Session without loss** — close the session, reopen it, disappear for a
  month: the agent resumes from exactly where you stopped, no
  re-explaining.
- **Switching costs nothing** — move between active modules and back
  without blending or losing either one's thread; each module keeps its
  own session state.
- **Full module history** — every session is preserved; reconstruct a
  module's whole timeline by reading from the start, not from memory.
- **Remember everything** — local or shared, knowledge is reachable from
  one agent window in the current session, no manual gathering first.
- **Find and use the best** — ask the agent to compare how other projects
  solve the same problem and apply the strongest approach, no
  hand-copying between them.
- **Agent knows what's checked** — every claim carries a confidence
  label, and the agent acts on it: confidently on a confirmed fact,
  cautiously on an unverified one.

A few more things you'll notice: a controlled test against a popular
flat-memory pattern for agents measured 30% lower cost even on small
projects — and the gap projects to be far larger on bigger ones. New
modules bootstrap from a template in minutes, not days — hand
`Templates/project-workspace/ASSEMBLY.md` to an agent and it runs the
same phases itself, including a module-inventory pass that keeps the
resulting knowledge base from starting too thin. And twice, unprompted,
the agent caught a real defect in its own knowledge base while doing
something else entirely.

## Why ERP

Deterministic Context Routing isn't ERP-specific — it's a response to four
difficulty axes that show up in any large codebase, and that ERP systems
tend to stack all at once:

- **Scale** — too much material exists to fit in a context window, so what
  gets routed in matters more than how much.
- **Opacity** — the real logic lives in table conventions, configuration,
  and business vocabulary, not in code a model can pattern-match against.
- **No compiler/runtime feedback** — nothing catches a wrong assumption
  automatically, so uncertainty has to be tracked explicitly instead of
  discovered by a build error.
- **No Git** — there's no commit history or blame to reconstruct intent
  from, so continuity has to live somewhere else.

Most large systems hit one or two of these. Proprietary ERP without Git or
a compiler hits all four at once — that's why it's the validation case,
not because the method only works there.

## Who This Is For

- ERP project teams and business analysts / architects working with
  proprietary or under-documented platforms.
- AI and agentic consultants building repeatable agent workflows for large,
  domain-heavy codebases.

## Quickstart

1. Copy `Templates/project-workspace/` into your project.
2. Fill root `idea.md`, then rename `modules/example-module/` and
   `knowledge-base/modules/example-module/` to your first real module.
3. Write that module's concept using the `templates/wiki/` module-concept
   template.
4. Curate your first table or class contract, and label every non-obvious
   claim with a confidence label.
5. Run one real task from that context, then update `session_state.md`
   before you stop.

Prefer to delegate? Hand `Templates/project-workspace/ASSEMBLY.md` to
your coding agent — it runs these steps phase by phase, checkpoints its
progress in `session_state.md`, and asks you only for the decisions.

For the full walkthrough, see
`Methodology/sections/12-practical-workspace-template.md`.

## How This Compares

**vs. Superpowers** — complementary, not competing. Superpowers is a
disciplined skills/workflow framework for how an agent executes a session
(brainstorming, planning, TDD, code review). This methodology is about what
domain context the agent should have before it starts.
`Methodology/sections/10-agentic-workflow-with-superpowers.md` covers
wiring the two together.

**vs. MCP** — MCP is a protocol for exposing tools and data sources to an
agent; it's a transport. This methodology is a curation discipline: which
facts are necessary and sufficient for a task, how confident you are in
each one, and where they live so the next session can find them again. You
can serve curated context to an agent over MCP — MCP doesn't decide what
belongs in that context.

**vs. LangChain / orchestration frameworks** — these orchestrate retrieval,
chains, and agent pipelines in code. This methodology is framework-agnostic:
a set of file-based conventions (module concepts, contracts, confidence
labels, session state) you can feed into any retrieval or orchestration
layer, including LangChain, or into no framework at all.

## In Good Company

- [Superpowers](https://github.com/obra/superpowers) solves session-level
  agent workflow discipline.
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) solves
  self-improving agent memory across sessions.
- This methodology solves the layer underneath both: project-level domain
  knowledge — what an agent needs to know about *this* system before either
  of the above can help.
- Validated on a large proprietary ERP platform in production use, where
  full source access, compiler/build tooling, and runtime checks were not
  available for most of the work.
- Self-tested on a second agent framework: the same graph-of-curated-pages
  structure — routing, confidence labels, session state, and the curation
  that builds the graph's edges — was re-tested by this project's author on
  [Hermes Agent](https://github.com/NousResearch/hermes-agent), a different
  agent product, on a non-ERP workspace. Self-run, not a Nous Research
  endorsement — see
  `Evidence/01-hermes-agent-cross-framework-validation.md`.

## Grounded In

The problems above aren't just this project's own experience — they show
up in independent research and industry material:

1. Oracle's own guidance on NL2SQL accuracy confirms that passing an
   unstructured or oversized schema into an LLM prompt degrades accuracy,
   and that curating table/column context beforehand is what fixes it —
   the same flood-vs-curate tradeoff this methodology is built around.
   ([Oracle: Best practices to improve NL2SQL accuracy with Select
   AI](https://blogs.oracle.com/machinelearning/best-practices-to-improve-nl2sql-accuracy-with-oracle-select-ai))
2. MIT NANDA's *State of AI in Business 2025* found that stalled enterprise
   GenAI pilots share one trait: "tools cannot retain feedback, adapt to
   context, or improve over time" — the exact continuity gap
   `session_state.md` exists to close. (The report's headline "95% of
   pilots fail" figure has been publicly disputed as unsupported by its
   own data; we're citing this specific, narrower finding, not that
   number.)
   ([MIT NANDA: The GenAI Divide — State of AI in Business
   2025](https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf))
3. A 2026 empirical benchmark on ABAP code generation found that LLM
   accuracy depends heavily on iterative compiler feedback — exactly the
   signal that's unavailable in the no-compiler case this methodology
   targets, which confidence labels are meant to compensate for.
   ([arXiv:2601.15188 — Benchmarking Large Language Models for ABAP Code
   Generation](https://arxiv.org/abs/2601.15188))

These sources back the *problem statement*. The methodology's mechanisms
have also been self-tested once, by this project's own author, on a
second agent framework and a non-ERP domain (see "In Good Company" above
and `Evidence/`) — that is a case study, not an independent third-party
audit or a peer-reviewed result.

## License

Licensed under the Business Source License 1.1 (see `LICENSE`), with an
Additional Use Grant for individuals, small teams (5 or fewer), and
non-commercial or educational use (see `ADDITIONAL-USE-GRANT.md`).
Commercial terms are in `COMMERCIAL-LICENSE.md`. Converts to MIT on
2030-07-03.

## Contributing

See `CONTRIBUTING.md`. Participation is governed by `CODE_OF_CONDUCT.md`.

---

*"Deterministic Context Routing" is an unregistered trademark of the
Licensor named in `LICENSE`.*
