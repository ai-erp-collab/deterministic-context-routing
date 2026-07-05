# Practical Adoption Checklist

## Goal

Apply the methodology to one module without trying to document the entire system first.

## 1. Select The Module

- [ ] Name the active module.
- [ ] Confirm its path in `modules.md`.
- [ ] Confirm wiki, source, and artifact roots.
- [ ] Read the module `AGENTS.md`.
- [ ] Read only the latest module `session_state.md` entry.

## 2. Record The Capability Profile

- [ ] State whether Git is available; if yes, name allowed status, diff, and history commands.
- [ ] State whether compiler/build verification is available; if yes, name the exact command.
- [ ] State whether automated tests are available; if yes, name the exact command and reliable scope.
- [ ] State whether local or target runtime checks are available.
- [ ] State required static or guardrail checks.
- [ ] Keep session-state updates mandatory because they record task intent, evidence, assumptions, verification, and next action.

## 3. Write The Module Concept

- [ ] State the module's business purpose.
- [ ] Define the main business terms.
- [ ] Name owned tables, documents, APIs, and workflows.
- [ ] Name neighboring modules and boundaries.
- [ ] Record unknowns explicitly.
- [ ] Label important mappings as `confirmed`, `inferred`, `runtime-unverified`, or `blocked-by-access`.

## 4. Curate One Evidence Artifact

- [ ] Put new raw exports in the configured raw artifact folder.
- [ ] Identify whether the artifact is a table schema, source example, user document, runtime note, or business rule.
- [ ] Create or refresh the smallest useful wiki page.
- [ ] Add confidence labels to important claims.
- [ ] Move processed table/source exports only after the wiki page is created or refreshed.
- [ ] Update the artifact index.

## 5. Run One Workflow-Backed Task

- [ ] Load only the module concept and the smallest relevant wiki pages.
- [ ] Write a short task plan before implementation.
- [ ] Record assumptions that cannot be verified locally.
- [ ] Make the smallest useful change.
- [ ] Run available Git inspection, compiler/build checks, automated tests, runtime checks, static checks, and guardrail scans according to the capability profile.

## 6. Record The Result

- [ ] Update module `session_state.md`.
- [ ] Update root `session_state.md` as a compact module activity index.
- [ ] Add durable discoveries to the module wiki or shared wiki.
- [ ] Add recurring workspace problems to `known_issues.md`.

## Done Criteria

- The next agent can identify the module, task state, evidence used, verification performed, and remaining assumptions without reading chat history.
- At least one curated page or durable note exists because of the task.
- The method has been proven on one narrow slice before wider rollout.
