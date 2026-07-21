# ASSEMBLY.md — Build This Workspace With an Agent

You are an agent assembling a methodology workspace from this template
for a real project. This file is your plan. The workspace's own
`session_state.md` is your progress tracker. Follow the phases in order.

Lines marked **ASK** are human decisions. Never resolve them yourself.

Assembly may take several sessions. That is expected; the continuity
protocol makes it safe.

## Continuity Protocol (read first, apply throughout)

1. After completing each phase, append an entry to `session_state.md`
   using `templates/session/`: phase number, what was produced, and
   "Next action: Phase N+1". End the entry with the stop marker line
   used by that template.
2. If you can observe your context usage and it exceeds ~40-50%, finish
   the current phase, write the checkpoint entry, and propose that the
   user restart the session. If you cannot observe context usage, rule 1
   already makes every phase boundary a safe stopping point.
3. On any session start: read `session_state.md` only to the first
   stop marker, find the recorded phase, and continue from the phase
   after it. Do not re-read completed phases' inputs.

## Inputs (ASK for any that are missing)

- Target folder for the new workspace.
- Path(s) to the project's code folder(s).
- Path(s) to the project's documentation folder(s), if separate.
- An existing `idea.md` or equivalent purpose/scope document, if any.

## Phase 0 — Copy the template

1. Copy this template folder's contents into the target folder.
2. Do not copy `ASSEMBLY.md`'s siblings from outside the template, and
   do not modify anything under the source code/docs paths — they are
   read-only inputs throughout assembly.
3. Verify the copy contains: `AGENTS.md`, `idea.md`, `known_issues.md`,
   `modules.md`, `session_state.md`, `knowledge-base/`,
   `source-artifacts/`, `modules/example-module/`, `templates/`.

Checkpoint: write the Phase 0 entry per the Continuity Protocol.

## Phase 1 — Continuity spine first: AGENTS.md and session_state.md

Adapt these two files before anything else, so the rest of assembly
runs under the workspace's own rules.

1. **ASK** the capability profile, one answer per line: Git available?
   Compiler/build? Automated tests? Runtime access? Static checks?
2. Record the answers in `AGENTS.md`'s capability profile section,
   replacing the template placeholders.
3. Copy the Continuity Protocol rules 1-3 above into `AGENTS.md` as the
   workspace's session rules (they remain the workspace's standing
   rules after assembly, not just during it).
4. Replace the template `session_state.md` example entry with your
   Phase 0 and Phase 1 entries.
5. Put the workspace rules into the file the target platform actually
   injects into session context at startup, and verify it empirically:
   ask a fresh session for a fact stated only in the rules file, with
   tool use forbidden. On Claude Code that file is `CLAUDE.md` at the
   workspace root — `AGENTS.md` alone is NOT injected (verified: an
   AGENTS.md-only workspace fails the check; the agent only finds the
   file if some tool call happens to lead it there). Other platforms
   have their own rules-file names and formats — check the platform's
   documentation, then run the same check. Rules the platform never
   loads do not exist for the agent — in particular the
   knowledge-access rules, which every question-answering session
   depends on.

Checkpoint: write the Phase 1 entry.

## Phase 2 — Project idea

1. If the user supplied an `idea.md` or equivalent: copy its content
   into the workspace root `idea.md`, adjusting to the template's
   headings.
2. If not: draft root `idea.md` yourself from the documentation and
   code folders — project purpose, scope, candidate modules, open
   questions. Keep every uncertain statement phrased as a question.
3. **ASK** the user to confirm or correct the draft. Do not proceed on
   an unconfirmed draft.

Checkpoint: write the Phase 2 entry.

## Phase 3 — Modules

1. From `idea.md` and the source folders, propose the module list:
   name, one-line purpose, source paths each module covers.
2. **ASK** the user to confirm module boundaries.
3. For the first confirmed module: rename `modules/example-module/` and
   `knowledge-base/modules/example-module/` to the module's name.
4. Create one folder pair per additional confirmed module by copying
   the renamed pair's structure.
5. Register every module in `modules.md` with its natural-language
   aliases.

Checkpoint: write the Phase 3 entry.

## Phase 4 — Raw material intake

1. Copy the project's documentation artifacts (specs, table exports,
   user documentation, business requirements) into
   `source-artifacts/*/raw/`, grouped by the registered modules.
2. Do not curate yet; intake only. Large sets are fine — raw is cheap.
3. List what was placed where in `source-artifacts/INDEX.md`.

Checkpoint: write the Phase 4 entry.

## Phase 5 — First curation runs (repeat per module, resumable)

For one module at a time:

1. Write the module concept page from `templates/wiki/`'s
   module-concept template, based on that module's raw materials.
2. Curate the module's most load-bearing artifacts first (a core table,
   contract, or usage flow), moving each processed source from raw
   toward processed per the workspace rules.
3. Label every non-obvious claim with a confidence label.
4. Checkpoint after each module — one module per session is a
   reasonable pace on large projects.

When all registered modules have at least a concept page and one
curated artifact, Phase 5 is done.

Checkpoint: write the Phase 5 entry (also per module, per rule above).

## Phase 6 — Verification and handoff

Confirm each item; fix before finishing if any fails:

1. `AGENTS.md` capability profile filled — no template placeholders
   remain anywhere in the workspace.
2. Root `idea.md` confirmed by the user.
3. Every module registered in `modules.md` has both folder pairs, a
   concept page, and at least one curated artifact.
4. `source-artifacts/INDEX.md` accounts for everything in raw.
5. Every non-obvious curated claim carries a confidence label.
6. `session_state.md` ends with a final entry: "Assembly complete;
   next action: first real task."

Tell the user assembly is complete and name the first real task you
would suggest. This file has done its job — the user may delete
`ASSEMBLY.md` from the workspace, or keep it for reference.
