# Project Workspace Template

This folder is a copyable starter kit for a file-based ERP agent workspace.

Copy these files into a new workspace, then replace placeholders such as
`<Project>`, `<Module>`, `<module-path>`, and `<source-root>` with project
values. Keep project-specific rules in clearly marked sections.

## Contents

- `ASSEMBLY.md`: agent-executable assembly guide — hand it to your agent to build the workspace; deletable after assembly.
- `AGENTS.md`: root workspace rules.
- `idea.md`: one-time project-level bootstrap input.
- `known_issues.md`: recurring workspace problems and required handling.
- `modules.md`: module registry and natural-language aliases.
- `session_state.md`: compact root activity index.
- `docs/superpowers/specs/`: design documents.
- `docs/superpowers/plans/`: implementation plans.
- `knowledge-base/shared/`: reusable cross-module knowledge.
- `knowledge-base/modules/example-module/`: example module wiki root.
- `source-artifacts/`: raw and processed source evidence.
- `modules/example-module/`: example module idea, instructions, and restart memory.
- `templates/wiki/`: module concept, table, contract, and usage-flow page templates.
- `templates/workflow/`: design and implementation-plan templates.
- `templates/session/`: session-state entry template.

## Adapting the Template

Hand `ASSEMBLY.md` to your agent — it runs the adaptation phase by
phase and asks you only for the decisions (capability profile, project
idea confirmation, module boundaries). To adapt by hand instead, follow
`Methodology/sections/12-practical-workspace-template.md`.
