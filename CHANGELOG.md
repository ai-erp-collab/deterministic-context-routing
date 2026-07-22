# Changelog

All notable changes to this repository are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning uses a draft `0.x` scheme until the methodology stabilizes;
backward-incompatible section renumbering or structural changes may still
occur before `1.0.0`.

## [0.4.0-draft] - 2026-07-22

### Added

- `Methodology/sections/02-emergent-capabilities.md` ("What You Get"): six
  reader-facing capabilities the method delivers — session continuity,
  cost-free module switching, full module history, single-window access to
  local/shared knowledge, cross-project reuse, and confidence-aware agent
  behavior — plus a shorter bonus block (measured cost savings, fast
  module bootstrap, incidental correctness auditing). Placed early in the
  reading order, right after the problem statement.
- `Methodology/sections/11-how-emergent-capabilities-work.md`: maps each of
  the six capabilities above to the specific mechanism that produces it,
  and to why a flat, always-loaded memory pattern cannot reproduce it.
  Placed after the agentic-workflow section, as a mechanism recap before
  the hands-on workspace-template section.
- A "What You Get" section in `README.md` and `uk/README.md`, summarizing
  the same six capabilities.
- A module-inventory phase (`ASSEMBLY.md` Phase 5) in
  `Templates/project-workspace/ASSEMBLY.md`: a flat, unfiltered per-module
  capture pass inserted between raw-material intake and curation, so
  curation selects from a complete list instead of from raw material
  directly. Documented in `Methodology/sections/12-practical-workspace-template.md`
  under a new "Agent-Delegated Assembly" subsection.

### Changed

- Renumbered every file in `Methodology/sections/` (and its `uk/` mirror)
  from the `02`-`12` range to `03`-`14` to make room for the two new
  sections; `00-preface.md`'s table of contents and reading-path ranges
  updated to match, in both languages.
- `Templates/project-workspace/ASSEMBLY.md`: existing curation and
  verification phases renumbered (5→6, 6→7) and cross-referenced against
  the new inventory phase.

## [0.3.0-draft] - 2026-07-21

### Added

- `Evidence/02-context-mechanism-vs-flat-memory-pattern.md`: a self-run
  comparison of Deterministic Context Routing against the Cline Memory Bank
  pattern (a flat, always-loaded memory set) on three real services, same
  model — completeness, navigation discipline (overread, re-discovery), and
  cost, plus a scaling projection to a larger reference project.
- `Templates/project-workspace/ASSEMBLY.md`: an agent-executable assembly
  guide — hand it to a coding agent to adapt the starter workspace phase by
  phase, checkpointing progress in `session_state.md` and asking the user
  only for the decisions that need one (capability profile, project idea
  confirmation, module boundaries).
- `Templates/project-workspace/AGENTS.md`: a knowledge-base-first retrieval
  rule — resolve the module and read its knowledge-base pages before
  re-reading raw sources or code, then record any recovered fact back into
  the knowledge base.

### Changed

- `README.md`: Quickstart now offers delegating to `ASSEMBLY.md` as an
  alternative to the manual steps.
- `Templates/project-workspace/README.md`: "First Adaptation Pass" reworked
  as "Adapting the Template," offering the `ASSEMBLY.md` guide as the
  primary path.

### Fixed

- `uk/README.md`: the "Curated Knowledge Base" pillar (added to the
  English README's Solution section in 0.2.0-draft) was missing from the
  Ukrainian translation — added.

## [0.2.0-draft] - 2026-07-08

### Added

- `Evidence/`: a new published folder for self-run test reports about the
  methodology, distinct from `Derivatives/` (which is generated from the
  methodology text rather than testing it). First entry: a cross-framework
  case study testing routing, confidence labels, session state, and
  curation on a second agent product (Hermes Agent, Nous Research) in a
  non-ERP domain.
- `uk/`: complete Ukrainian-language translation of the methodology
  sections, `Derivatives/`, and `README.md`, with a language-switch link
  added to the top of the English README.
- A fourth "Curated Knowledge Base" pillar in the README's Solution
  section, naming the curation step that was previously only implicit in
  the diagram and the Quickstart.

### Changed

- Hero diagram redesigned as a theme-adaptive (light/dark) three-panel
  methodology overview (Deterministic Routing / Layered Memory System /
  Agent Engine & Gates), replacing the original single-file flow diagram.
- README's "In Good Company" and "Grounded In" sections updated to
  reference the new cross-framework case study instead of stating the
  methodology "hasn't been independently evaluated by a third party."

## [0.1.0-draft] - 2026-07-04

### Added

- Initial public release of the Deterministic Context Routing methodology:
  13 sections covering the knowledge system, module concept, knowledge
  acquisition, table and library contracts, usage flows, the agentic
  workflow, the practical workspace template, the KB curator workflow, and
  the adoption bootstrap and template audit.
- `Derivatives/`: executive brief, practical adoption checklist, and public
  article outline.
- `Templates/project-workspace/`: copyable starter workspace, including
  root rules, module registry, session-state template, and wiki/workflow
  templates.
- `Templates/section-contract.md` and `Templates/section-dod.md`: the
  authoring standard every methodology section is written against.
- Licensing: Business Source License 1.1 with an Additional Use Grant for
  small, non-commercial, and educational use, converting to MIT on
  2030-07-03.
