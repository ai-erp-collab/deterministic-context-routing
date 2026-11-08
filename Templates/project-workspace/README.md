# Project Workspace Template

This folder is a copyable starter kit for a file-based agent workspace on any codebase; large proprietary ERP is the proof case.

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
- `source-artifacts/`: copies of source evidence. `registry.json` is the ledger (origin path, hash,
  status); `INDEX.md` is generated from it. Files never move after intake: `raw` or `processed` is
  a status in the registry, not a folder change.
- `tools/kb/`: the knowledge-base integrity tool (`python tools/kb/kb.py <command>`, Python 3.9 or
  later, standard library only). Code only: an upgrade replaces it.
- `.kb/`: the tool's project data (config, table-export profiles, journal of automatic edits,
  lookup index). Created by `python tools/kb/kb.py upgrade --yes`; an upgrade never overwrites it.
- `.codex/hooks.json`: Codex hooks that run the tool's checks after edits, at stop, and at
  session start.
- `modules/example-module/`: example module idea, instructions, and restart memory.
- `templates/wiki/`: module concept, table, contract, usage-flow, and glossary-term page templates.
- `templates/workflow/`: design and implementation-plan templates.
- `templates/session/`: session-state entry templates, including the cross-module entry left in an owner module.
- `skills/`: platform-neutral agent skills; `cross-module-owner-api` handles work that reaches from the active module into another module; `kb` resolves what the integrity tool reports and holds its procedures. Install them where your agent platform loads skills (a Codex copy of `kb` ships in `.codex/skills/kb/`).

## Adapting the Template

Hand `ASSEMBLY.md` to your agent — it runs the adaptation phase by
phase and asks you only for the decisions (capability profile, project
idea confirmation, module boundaries). To adapt by hand instead, follow
`Methodology/sections/12-practical-workspace-template.md`.
