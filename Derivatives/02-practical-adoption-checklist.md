# Practical Adoption Checklist

## Goal

Apply the methodology to one module without trying to document the entire system first.

## 1. Select The Module

- [ ] Name the active module.
- [ ] Confirm its path in `modules.md`.
- [ ] Confirm wiki, source, evidence, and artifact roots.
- [ ] Read the module `AGENTS.md`.
- [ ] Read only the latest module `session_state.md` entry.

## 2. Record The Capability Profile

- [ ] State whether Git is available; if yes, name allowed status, diff, and history commands.
- [ ] State whether compiler/build verification is available; if yes, name the exact command.
- [ ] State whether automated tests are available; if yes, name the exact command and reliable scope.
- [ ] State whether local or target runtime checks are available.
- [ ] State required static or guardrail checks.
- [ ] Keep session-state updates mandatory because they record task intent, evidence, assumptions, verification, and next action.

## 2a. Install The Integrity Layer

- [ ] Install the workspace tool `tools/kb/` (the `context-routing` plugin does it in one step) and confirm Python 3.9 or later is available.
- [ ] Install the hooks for the agent in use; on Codex, trust the project hooks with `/hooks`.
- [ ] For a workspace built with an earlier template, run `kb upgrade --dry-run`, review the plan (including legacy link conversions) with the user, then apply it.
- [ ] Exclude links that point outside the workspace on purpose with a `link_ignore` glob in `.kb/config.json` (matched against the link as written, for example `*other-repo/*`) or `<!-- kb:ignore-link -->` on the line.

## 3. Write The Module Concept

- [ ] State the module's business purpose.
- [ ] Define the main business terms.
- [ ] Name owned tables, documents, APIs, and workflows.
- [ ] Name neighboring modules and boundaries.
- [ ] Record unknowns explicitly.
- [ ] Label important mappings as `confirmed`, `inferred`, `runtime-unverified`, or `blocked-by-access`.

## 4. Curate One Evidence Artifact

- [ ] Register new exports with `kb ingest` (a hashed copy and a registry row); never copy them by hand.
- [ ] Identify whether the artifact is a table schema, source example, user document, runtime note, or business rule.
- [ ] Look for an existing page with `kb resolve` before writing a new one.
- [ ] Create or refresh the smallest useful wiki page; for a table export use `kb table`.
- [ ] Add confidence labels to important claims.
- [ ] Name the evidence copy in the page's `source:` line so its registry row becomes `processed`; never move evidence files.

## 5. Run One Workflow-Backed Task

- [ ] Load only the module concept and the smallest relevant wiki pages.
- [ ] Write a short task plan before implementation.
- [ ] Record assumptions that cannot be verified locally.
- [ ] Make the smallest useful change.
- [ ] If the task needs a rule another module owns, reach into that module only on your question (read only) or command (change allowed): call its owner API instead of copying the rule, once you act on it, link the owner contract page from this module (a plain question leaves no link), and leave a cross-module mark in the owner module.
- [ ] Run available Git inspection, compiler/build checks, automated tests, runtime checks, static checks, and guardrail scans according to the capability profile.

## 6. Record The Result

- [ ] Run `kb check --changed <files>` and resolve or queue what it lists.
- [ ] Update module `session_state.md`.
- [ ] Update root `session_state.md` as a compact module activity index.
- [ ] Add durable discoveries to the module wiki or shared wiki.
- [ ] Add recurring workspace problems to `known_issues.md`.

## Done Criteria

- The next agent can identify the module, task state, evidence used, verification performed, and remaining assumptions without reading chat history.
- At least one curated page or durable note exists because of the task.
- `kb check` reports no blocking issues; open issues are numbered in `docs/checks/OPEN.md`.
- The method has been proven on one narrow slice before wider rollout.
