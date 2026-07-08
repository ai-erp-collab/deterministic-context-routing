# Changelog

All notable changes to this repository are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning uses a draft `0.x` scheme until the methodology stabilizes;
backward-incompatible section renumbering or structural changes may still
occur before `1.0.0`.

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
