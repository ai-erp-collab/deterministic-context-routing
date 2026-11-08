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
   after it. If the latest entry is `Phase 0 started`, repeat Phase 0:
   the copy was interrupted. Do not re-read completed phases' inputs.

## Existing Workspace? Upgrade Instead

If the target folder already holds a workspace (it has both
`AGENTS.md` and `modules.md`) that has no `Phase 0 started` entry in
its `session_state.md`, do not run the phases below. It was built with
an earlier template. Copy this template's `tools/kb/` into it, then:

1. Run `python tools/kb/kb.py upgrade --dry-run --from <this template folder>`.
   It prints the plan: files to add or replace, project-edited files
   (kept; a `<file>.new` is written beside them), the managed block,
   hook entries, data migrations, legacy `[[...]]` link conversions,
   links in `AGENTS.md` and session logs that will not open,
   and questions. Nothing is written.
2. Show the whole plan to the user, including the link conversions.
   **ASK** each question it lists (for example evidence folders per
   module) and **ASK** for approval of the plan.
3. Run the same command with the answers and `--yes`. It snapshots
   the workspace first; `kb upgrade --rollback` returns to that state.
4. Merge every `<file>.new` into its file, keeping the project's edits.
5. On Codex, tell the user to trust the project hooks with `/hooks`.
6. Write a `session_state.md` entry with the before/after counts the
   upgrade printed. Assembly is then complete.

## Inputs (ASK for any that are missing)

- Target folder for the new workspace.
- Path(s) to the project's code folder(s).
- Path(s) to the project's documentation folder(s), if separate.
- An existing `idea.md` or equivalent purpose/scope document, if any.

## Phase 0 — Copy the template

1. Before copying anything, start the log: if the target has no
   `session_state.md`, copy the template's one and delete its example
   entry; then add an entry titled `Phase 0 started` at its top, so an
   interrupted copy is resumed and never mistaken for a finished
   workspace. Copy the remaining template contents into the target
   folder, skipping files that already exist there (list them).
2. Do not copy `ASSEMBLY.md`'s siblings from outside the template, and
   do not modify anything under the source code/docs paths — they are
   read-only inputs throughout assembly.
3. Verify the copy contains: `AGENTS.md`, `idea.md`, `known_issues.md`,
   `modules.md`, `session_state.md`, `knowledge-base/`,
   `source-artifacts/`, `modules/example-module/`, `templates/`,
   `skills/`, `tools/kb/kb.py`, `.codex/hooks.json`.
4. Check that `python --version` (or `python3 --version`, or
   `py -3 --version`) reports 3.9 or later. If not, **ASK** the user whether to continue without the
   integrity tool: the workspace still works, but no checks run.

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
6. Install the skills from `skills/` where the target platform loads
   skills (for example `.claude/skills/` or `.codex/skills/`); if the
   platform has no skill mechanism, keep the folder and make sure the
   rules file points to the skill file by path. Verify that a fresh
   session can name the `cross-module-owner-api` skill when asked
   whether another module already has some rule. On Codex the `kb`
   skill is already in `.codex/skills/kb/`.
7. Run `python tools/kb/kb.py upgrade --yes` (it writes `.kb/` and the
   managed block of the rules file), then `python tools/kb/kb.py doctor`.
   On Codex, tell the user to trust the project hooks with `/hooks`.

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
6. **ASK** per module for evidence folders (table exports, library
   sources, usage examples, documents) and record them as an
   `evidence:` line after `sources:`; omit the line when there are none.

Checkpoint: write the Phase 3 entry.

## Phase 4 — Raw material intake

1. Take in the project's documentation artifacts (specs, table
   exports, user documentation, business requirements) per module with
   `python tools/kb/kb.py ingest <path...> --module <Module> --kind <kind>`.
   It copies them into `source-artifacts/`, records origin and hash in
   `registry.json`, and regenerates `source-artifacts/INDEX.md`.
2. Do not curate yet; intake only. Large sets are fine — raw is cheap.

Checkpoint: write the Phase 4 entry.

## Phase 5 — Module inventory (repeat per module, before curation)

Before writing any curated wiki page, capture everything the raw
material contains, unfiltered. This phase exists because selecting
"the most load-bearing" material on a first pass silently drops real
facts that later turn out to matter — the inventory removes that
selection pressure by capturing everything first, then letting
curation select from a complete list instead of from raw material.
This is not optional: a curator that skips straight to selective
curation reliably writes too little for the resulting pages to
support real task work, which is why this phase has no alternative.

For one module at a time:

1. Read every raw artifact placed for this module in Phase 4, in
   full — not selectively, not "enough to get the gist."
2. Write one flat inventory page,
   `knowledge-base/modules/<module>/inventory.md`, listing every
   named mechanism, function, flag, constant, convention, naming
   rule, or constraint found, one line each, with the source file it
   came from. Do not organize this page into concept/contract/table
   structure and do not omit an item because it seems minor, rare,
   internal, or already implied elsewhere in the raw
   material — completeness, not readability, is this page's only
   job.
3. Do not judge importance yet. If in doubt whether something is
   named prominently enough to count, include it — Phase 6 is where
   selection and structure happen, not this phase.
4. Checkpoint after each module — one module per session is
   reasonable pace, same as Phase 6.

When all registered modules have an inventory page, Phase 5 is done.

Checkpoint: write the Phase 5 entry.

## Phase 6 — First curation runs (repeat per module, resumable)

For one module at a time:

0. Read the module's `inventory.md` from Phase 5 before writing any
   page — it is the checklist this phase works against.
1. Write the module concept page from `templates/wiki/`'s
   module-concept template, based on that module's raw materials.
2. Curate the module's most load-bearing artifacts first (a core table,
   contract, or usage flow). Each page names its artifact copy in its
   `source:` line; the integrity tool then records that artifact as
   processed. Files stay where intake put them. Every item on the
   module's `inventory.md` must end up on a concept/contract/table
   page, or be marked in `inventory.md` itself as deliberately
   excluded (e.g. internal, deprecated, out of scope) with a one-line
   reason. Load-bearing material first is still the right drafting
   order; every item still accounted for is the new requirement.
3. Label every non-obvious claim with a confidence label.
4. Checkpoint after each module — one module per session is a
   reasonable pace on large projects.

When all registered modules have at least a concept page and one
curated artifact, Phase 6 is done.

Checkpoint: write the Phase 6 entry (also per module, per rule above).

## Phase 7 — Verification and handoff

Confirm each item; fix before finishing if any fails:

1. `AGENTS.md` capability profile filled — no template placeholders
   remain anywhere in the workspace.
2. Root `idea.md` confirmed by the user.
3. Every module registered in `modules.md` has both folder pairs, a
   concept page, and at least one curated artifact.
4. `python tools/kb/kb.py check` reports no blocking issues, and its open
   issues are listed to the user (minor ones, such as evidence still
   waiting to be processed, are expected after intake).
5. Every non-obvious curated claim carries a confidence label.
6. Every line in every module's `inventory.md` is either represented
   on a curated page or explicitly marked excluded with a reason —
   spot-check by grepping a sample of inventory items against the
   curated pages.
7. The `cross-module-owner-api` and `kb` skills are installed or
   referenced by path, and the rules file names them. The rules file
   holds the `<!-- kb:begin -->` block. On Codex the user has trusted
   the project hooks (`/hooks`); elsewhere the agent's hooks are
   installed, or the user knows the checks run only through the
   rules-file lines.
8. `session_state.md` ends with a final entry: "Assembly complete;
   next action: first real task."

Tell the user assembly is complete and name the first real task you
would suggest. This file has done its job — the user may delete
`ASSEMBLY.md` from the workspace, or keep it for reference.
