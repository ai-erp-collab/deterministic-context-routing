# Project Workspace Template

This folder is a copyable starter kit for a file-based ERP agent workspace.

Copy these files into a new workspace, then replace placeholders such as
`<Project>`, `<Module>`, `<module-path>`, and `<source-root>` with project
values. Keep project-specific rules in clearly marked sections.

## Contents

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

## First Adaptation Pass

1. Fill root `idea.md` with the project purpose, scope, first modules, and open questions, then use it to create durable starter artifacts.
2. Rename `modules/example-module/` and `knowledge-base/modules/example-module/`.
3. Fill the module `idea.md` with the module purpose, users, capabilities, boundaries, and first requests, then turn it into a module concept.
4. Register the real module in `modules.md`.
5. Replace project-specific examples in `AGENTS.md` and `known_issues.md`, including the capability profile for Git, compiler/build, tests, runtime access, and static checks.
6. Write the first module concept from `templates/wiki/module-concept-page.md`.
7. Add one real artifact to `source-artifacts/tables/raw/`.
8. Curate one table, contract, or usage page before moving that artifact to processed.
