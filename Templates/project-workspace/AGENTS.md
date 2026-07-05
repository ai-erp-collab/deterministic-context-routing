# Workspace Rules

- Read `known_issues.md` before non-trivial work.
- Read `modules.md` to resolve module names, aliases, paths, wiki roots, source roots, and artifact roots.
- If the active module is unclear, ask which module to use.
- If no module is explicitly requested, continue with the last active module named in root `session_state.md`.
- Read the active module `AGENTS.md` before non-trivial work.
- Read only the latest entry in the active module `session_state.md`: stop at the first line that exactly equals `<!-- AGENT-SESSION-STOP -->`.
- Keep module-specific durable knowledge in `knowledge-base/modules/<module>`.
- Keep reusable platform or cross-module knowledge in `knowledge-base/shared`.
- Keep raw source artifacts separate from curated knowledge.
- Update the active module `session_state.md` after every non-conversational task.
- Update root `session_state.md` only as a compact module activity index.
- When full automated testing is impossible, document static checks and remaining runtime assumptions.
- Keep `session_state.md` even when Git exists; Git records file history, while session state records task intent, evidence, assumptions, verification, and next action.

## Project-Specific Rules

- Capability profile:
  - Git: define whether `git status`, `git diff`, and recent history may be used, or state that Git is unavailable.
  - Compiler/build: define exact commands when available, or state that compiler/build verification is unavailable.
  - Automated tests: define exact commands and reliable scope, or state that tests are unavailable or incomplete.
  - Runtime access: define local or target-environment checks, or state that runtime behavior must be marked runtime-unverified.
  - Static/guardrail checks: define required scans and commands.
- Example: define privacy, data access, encoding, or deployment constraints here.
- Example: define how raw artifacts move from raw to processed here.

## Bootstrap Note

- Root `idea.md` is a one-time starting input. Use it when the user asks you to bootstrap the project from an idea, then move durable meaning into `modules.md`, module concepts, wiki pages, plans, and session state.
