# Adoption Bootstrap And Template Audit


## Reader Outcome

After this section, the reader can:

- Bootstrap the methodology in another project without relying on chat history.
- Decide what to copy, what to adapt, and what to mark project-specific.
- Run the first module setup, first curation pass, and first workflow-backed task.
- Audit the guide against the starter templates.
- Identify claims in the guide that are unsupported by actual template artifacts.
- Install the integrity layer's hooks for the agent in use, and know what happens when hooks cannot run.
- Apply the fix policy: which edits the tool makes alone, which it hands to the agent, and how every automatic edit is undone.
- Migrate an existing wiki and upgrade a workspace built with an earlier template without losing project edits.

## Core Explanation

Adoption should end with a usable workspace, not only agreement with the method.

The safest path is incremental: start from a project or module idea, create the starter structure, register one module, write one module concept, normalize one small artifact or source contract, run one workflow-backed task, update documentation, and then audit the template package. This proves that the guide is executable and that its examples are grounded in real files.

The audit is part of the method. It catches two kinds of drift:

- the guide promises an artifact that the starter kit does not provide;
- the starter kit contains a template or rule that the guide never explains.

It also separates universal guidance from project-specific examples. Encoding rules, SQL dialect details, proprietary runtime constraints, source roots, table parsers, build limitations, compiler availability, version-control availability, and runtime access should be labeled as project requirements, not sold as universal methodology.

## Integrity Layer In Adoption

Section 03 explains why mechanical upkeep moves into code. Adoption decides whether that code actually runs. This part covers four things: hooks, the fix policy, migrating an existing wiki, and upgrading a workspace across template versions.

### Hooks Per Agent

The checks run on three events, with no agent memory involved:

- After an edit to a page or to evidence, the hook applies safe fixes to the changed file and checks it. It prints nothing when the file is clean, and one short message with the remaining issues otherwise.
- At the end of a turn, the hook checks the files changed in the session. If they introduced a blocking issue, it stops the turn once with the issue lines; it never stops the same turn twice, so it cannot trap the agent in a loop.
- At session start, the hook prints one line when issues are open or when the workspace is older than the installed tool.

Hook messages name the `kb` skill, so the agent is pulled into the right procedure by the event, not by remembering a rule. Each agent platform wires hooks differently. Claude Code receives them from the `context-routing` plugin; in a folder without the tool they do nothing, except that a workspace built with an earlier template gets a one-line hint to upgrade. Codex reads them from the workspace file `.codex/hooks.json`; project hooks run only after the user trusts them with `/hooks`, so the setup step asks the user to do that. Cursor, OpenCode, Antigravity, and Hermes get no hooks from this package; there the checks run by hand through the fallback below. Every hook looks for Python 3.9 or later under the usual command names and exits silently when none is found, so a machine without a usable interpreter loses the checks but never breaks the agent.

Hooks may be unavailable: a platform without hook support, a policy that blocks them, or a session started in a subfolder. The fallback is the two lines in the managed block of `AGENTS.md` (outline large files; run `kb check --changed` before closing a session) and the session-closing step, which runs the same check and records its result in `session_state.md`. The fallback costs a little attention; the hooks cost none.

### Fix Policy

An automatic edit is allowed only when exactly one correct answer exists and code can compute it:

- a link, including a legacy `[[...]]` link, whose file name matches exactly one file inside the linking page's own area (its module wiki, the shared wiki, or the knowledge base), with the folder names the link spells out;
- a page missing from its folder `INDEX.md`;
- an evidence file without a registry row (added as `raw`);
- a registry row still `raw` although a curated page already names the copy in its `source:` line (marked `processed`);
- a stale lookup index.

Everything else is ambiguous: several candidates, no candidate, or facts that conflict. The tool never edits those; it opens an issue that lists the candidates. Session logs are never fixed automatically, because they are history. In rules files such as `AGENTS.md`, a link is fixed automatically only when its own path resolves; a fix found by searching file names is proposed, not applied, because a rule there may name a file in general rather than one module's copy. A proposed fix with a single target can be applied on request with `kb fix --ids <N>`.

Every automatic edit is appended to `.kb/journal/` with its run id, file, text before, text after, and the rule that made it. `kb undo <run-id>` reverts one run if the files have not changed since. `kb fix --safe --dry-run` prints the edits without making them. The result is that automatic edits are frequent, small, visible, and reversible, while anything that needs judgment stays with the agent and the user.

### Migrating An Existing Wiki

A project that already has a wiki usually has links written for a wiki viewer (`[[Page Name]]`), pages missing from indexes, and evidence that was never registered. The first run on such a wiki always starts with a preview. The upgrade plan described next counts how many `[[...]]` links become relative links and how many stay as issues, with examples, and the user approves the plan before anything changes. A conversion is applied only when the target is unique and lies in the linking page's own area; every other link becomes an issue with its candidates. All conversions are journaled and undone together by the upgrade rollback.

### Upgrading A Workspace Across Versions

Workspaces built with an earlier template must reach the current one without losing project edits and without manual work beyond answering questions. The command is `kb upgrade`; the plugin's setup skill switches to it when it finds an existing workspace.

1. Preview. `kb upgrade --dry-run` prints the plan: files to add or replace, files the project has edited, the managed block, hook entries to merge, numbered data migrations, link conversions, links in rules files and session logs that will not open (they become blocking issues once those files are checked), and questions (for example, the evidence folders of each module). Nothing is written. The user approves the plan once.
2. Snapshot. The upgrade zips the knowledge base, the module registry, the evidence registry and index, the rules files, skills, and hooks into `.kb/backups/` before it changes anything. Large evidence copies are listed rather than zipped. This is the rollback point when the project has no version control.
3. Shipped files. A manifest records the hash of every file the template installed. A file that is absent is added; a file unchanged since installation is replaced; a file the project edited is kept, and the new version is written beside it as `<file>.new` with an issue to merge it. A project edit is never overwritten.
4. Managed blocks. Rules files receive the tool's lines between `<!-- kb:begin -->` and `<!-- kb:end -->`; later upgrades replace only that block. Hook files are merged by entry, keeping the project's own hooks.
5. Data migrations. Numbered, idempotent steps convert older data: evidence folders added to `modules.md` after the user confirms them, the old artifact index imported into the registry, legacy links converted as previewed, `.kb/` defaults written, the lookup index built, and old skill copies in `skills/` and `.codex/skills/` moved to `.agents/skills/` (copies the project edited are kept and reported for a manual merge). Running a migration twice changes nothing.
6. Verify. A full check runs, and the upgrade reports before-and-after counts (valid links, duplicate groups, untracked evidence, open issues).

Each step is recorded in an upgrade log in `.kb/`, so an interrupted upgrade continues where it stopped; the agent also writes a `session_state.md` entry with the reported counts. `kb upgrade --rollback` restores the snapshot and reverses the upgrade's journaled edits. If any file changed after the upgrade, it refuses, lists those files, and changes nothing, so later curation is never lost. A later template version adds a migration and raises the workspace version; the same command then upgrades across several versions in order.

## Bootstrap Procedure

1. Create the starter workspace.
   - Add root instructions, root idea, known issues, module registry, root session state, docs folders, knowledge roots, source artifact roots, and one module folder.
   - Copy only the universal parts of the instruction templates.
   - Install the integrity layer: the plugin does it in one step; with the template, copy `tools/kb/`, the `.agents/skills/` folder, and `.codex/hooks.json`, run `python tools/kb/kb.py upgrade --yes` once, then `python tools/kb/kb.py doctor`. On Codex, ask the user to trust the project hooks with `/hooks`.
   - If the target already is a workspace (it has `AGENTS.md` and `modules.md`), upgrade it instead: preview with `kb upgrade --dry-run`, get the user's approval, then apply.

2. Write the project idea.
   - State why the workspace exists, who it serves, which business areas are in scope, which first modules are expected, what evidence is available, and which open questions shape the first dialogue.
   - Treat this as one-time bootstrap input. After the first artifacts exist, durable meaning belongs in the module registry, module concept, wiki pages, plans, and session state.

3. Add project-specific rules.
   - Record a capability profile for Git, compiler/build, automated tests, runtime access, static checks, encoding, SQL/runtime, source access, privacy, deployment, and other tooling constraints.
   - Mark them as project-specific.
   - Add required verification commands when the project has them.
   - Keep session-state updates mandatory even in Git-enabled projects because commits and logs are not reliable task-continuity memory.

4. Register the first module.
   - Add canonical name, aliases, module path, wiki root, shared wiki root, source roots, evidence folders, artifact roots.
   - Create module idea, module instructions, and module session state.

5. Write the first module idea.
   - State the module's purpose, primary users and actors, business capabilities, boundaries, core terms, common starting requests, first evidence, open questions, and first useful next step.
   - For existing mature modules, this can be replaced by a short audit of where the same intent already lives.

6. Write the first module concept.
   - Keep it short.
   - Define purpose, boundaries, core entities, terms, intent patterns, invariants, and links.
   - Mark unknown mappings instead of inventing them.

7. Run the first curator pass.
   - Choose one real knowledge need.
   - Search existing knowledge first.
   - Inspect the smallest relevant evidence.
   - Create one table, contract, or usage page.
   - Update indexes and session state.

8. Run the first workflow-backed task.
   - Use Superpowers or an equivalent workflow.
   - Feed it the module concept, relevant contracts, usage flows, assumptions, and verification limits.
   - Update durable knowledge when the task changes behavior.

9. Verify and record limits.
   - Run available static checks.
   - Use Git, compiler/build commands, automated tests, or runtime checks when the capability profile says they are available.
   - Run project guardrail checks such as encoding scans when required.
   - Run `python tools/kb/kb.py check`; resolve blocking issues and list the open ones to the user.
   - Record runtime-unverified assumptions.
   - Update root and module session state.

10. Run the template audit.
   - Compare guide requirements with actual template files.
   - Compare actual templates with guide explanations.
   - Label unsupported or project-specific material.

## Template Audit

Use this audit before publishing or copying the starter kit.

### Guide Mentions That Need Templates

The guide names these reusable artifacts. The starter kit should include them or clearly mark them optional:

- module concept page;
- table page;
- class or function contract page;
- usage flow page;
- design doc;
- implementation plan;
- session-state entry.

Recommended bootstrap inputs:

- project idea document;
- module idea document.

In this project, these are present in `Methodology/Templates/project-workspace/`:

- `wiki/module-concept-page.md`;
- root `idea.md`;
- `modules/example-module/idea.md`;
- `wiki/table-page.md`;
- `wiki/contract-page.md`;
- `wiki/usage-flow-page.md`;
- `workflow/design-doc.md`;
- `workflow/implementation-plan.md`;
- `session/session-state-entry.md`;
- `wiki/glossary-term-page.md`.

The copyable project workspace in `Methodology/Templates/project-workspace/` also includes root starter files, an example module, knowledge roots, source artifact folders, and workflow folders.

### Templates That Need Guide Coverage

Every shipped template should be explained by the guide:

- `project-workspace/idea.md`: covered as the project starting dialogue.
- `project-workspace/modules/example-module/idea.md`: covered as the module starting dialogue.
- `project-workspace/templates/wiki/module-concept-page.md`: covered by module language and adoption bootstrap.
- `project-workspace/templates/wiki/table-page.md`: covered by table contracts and curator workflow.
- `project-workspace/templates/wiki/contract-page.md`: covered by class contracts and curator workflow.
- `project-workspace/templates/wiki/usage-flow-page.md`: covered by usage flows and curator workflow.
- `project-workspace/templates/workflow/design-doc.md`: covered as workflow artifact, not durable ERP truth.
- `project-workspace/templates/workflow/implementation-plan.md`: covered as workflow artifact, not durable ERP truth.
- `project-workspace/templates/session/session-state-entry.md`: covered as compact restart context.
- `project-workspace/templates/wiki/glossary-term-page.md`: covered by shared terms in module language.
- `project-workspace/tools/kb/`: covered by the integrity layer in the knowledge system, the workspace template, and this section.
- `project-workspace/.agents/skills/kb/`: covered as the one skill hook messages point to.
- `project-workspace/.agents/skills/`: covered as the skill folder most agent platforms read as project skills.
- `project-workspace/.codex/hooks.json`: covered by hooks per agent in this section.
- `section-contract.md`: project-specific to this Methodology module's section-writing workflow.
- `section-dod.md`: project-specific to this Methodology module's section quality gate.

### Project-Specific Material

When publishing the guide, mark these as project examples unless they are true for the target project:

- absence of git;
- absence of local compiler or build verification;
- UTF-8 and Cyrillic encoding scan;
- exact evidence folders in `modules.md`;
- exact source roots such as platform or project library folders;
- exact table parsers;
- proprietary runtime limitations;
- source-origin wording constraints;
- module names and aliases.

### Missing Or Optional Templates

The guide also discusses artifacts that may not need standalone templates in every project:

- root `AGENTS.md`;
- module `AGENTS.md`;
- `modules.md`;
- `known_issues.md`;
- artifact index;
- shared or module `INDEX.md`;
- pattern page.

In this project, the published starter kit includes root `idea.md`, module `idea.md`, root `AGENTS.md`, module `AGENTS.md`, `modules.md`, `known_issues.md`, root and module `session_state.md`, source artifact index, shared and module `INDEX.md` files, and artifact folders. The idea files are bootstrap inputs, not recurring operational memory. The starter kit does not include a standalone pattern page template; pattern pages remain optional unless a target project needs them.

If additional artifacts become part of the published starter kit, add templates. If not, keep them as examples with enough inline structure for the reader to create them.

## Reproducible Procedure

1. Follow the bootstrap procedure for one module.
2. Produce at least one curated page from real evidence.
3. Run one workflow-backed task or documentation task.
4. Update session state and verification notes.
5. Run the template audit.
6. Resolve gaps by either adding templates, explaining existing templates, or marking artifacts optional/project-specific.

## Required Artifacts

- Root starter files.
- First module registration.
- First module concept.
- At least one curated page from real evidence.
- Updated indexes.
- First workflow artifact set.
- Verification record.
- Template audit result.
- Root and module session-state entries.
- Copyable starter workspace package when publishing outside the current project.

Recommended for new bootstrap:

- Root project idea.
- First module idea.

## Example

For a new ERP project, start with one module, not the whole system.

1. Register `Budgeting` with aliases such as budget and planning.
2. Fill root `idea.md` with project purpose, first modules, evidence, and open questions.
3. Create `Budgeting/AGENTS.md`, `Budgeting/idea.md`, and `Budgeting/session_state.md`.
4. Write `Budgeting Concept` with purpose, boundaries, core entities, and common user requests.
5. Register one table export with `kb ingest`.
6. Use the curator workflow and `kb table` to create one table contract; the registry row becomes `processed` once the page names the copy.
7. Document one access or posting usage flow.
8. Run one small feature or documentation task through the workflow.
9. Run `kb check`, resolve what it lists, and update session state.
10. Run the template audit.

This proves the process on a narrow slice before scaling it across modules.

For an existing workspace with a hand-kept wiki, the same project starts differently: `kb upgrade --dry-run` shows, say, several hundred `[[...]]` links of which most convert and a few dozen stay as issues because two pages share a name; the user approves; the upgrade snapshots, converts, imports the old artifact index into the registry, and reports the before-and-after counts. The issues that remain are judgment calls (which of two same-named pages a link meant), worked through the queue over the following sessions.

## Failure Modes

- Trying to document every module before proving the workflow on one module.
- Copying project-specific rules into another project without review.
- Skipping explicit project or module intent, so the first dialogue starts without business purpose.
- Skipping the first module concept and starting from raw source.
- Creating raw artifact folders but never creating curated pages.
- Treating workflow designs and plans as permanent contracts.
- Publishing guide text that references templates not included in the starter kit.
- Shipping templates that no section explains.
- Shipping a starter kit with placeholders that are not documented as placeholders.
- Skipping runtime-assumption records because static checks passed.
- Using the hard-case workflow in a project that has Git, compiler/build checks, tests, or runtime access.
- Treating commit history as a substitute for session state.
- Installing the tool without its hooks, leaving Codex hooks untrusted, or skipping the manual check on an agent without hooks: the checks exist but never run.
- Running the first fix on an existing wiki without a preview: hundreds of links change before anyone has seen the plan.
- Overwriting shipped files the project edited during an upgrade: project rules disappear silently.
- Hand-editing inside the managed block: the next upgrade replaces it.
- Upgrading without a snapshot on a project without version control: there is no way back.

## Assumptions And Runtime Limits

- Adoption is iterative; the first version can be partial if uncertainty is explicit.
- The target project may have different runtime, source access, encoding, or verification constraints.
- The target project may have Git, a compiler, automated tests, or runtime access; when present, those capabilities should strengthen verification but not replace session state.
- A starter kit should prefer small templates and real examples over broad claims.
- The audit checks consistency, not correctness of business behavior.
- Whether a given agent platform runs project hooks under a given security policy must be confirmed on that machine; the fallback lines keep the method working when it does not.

## Related Notes

- `04-workspace-bootstrap.md`: conceptual bootstrap background.
- `10-agentic-workflow-with-superpowers.md`: recommended workflow boundary.
- `12-practical-workspace-template.md`: practical starter workspace template.
- `03-knowledge-system.md`: knowledge-base degradation and the deterministic integrity layer.
- `13-kb-curator-and-artifact-workflow.md`: curator and artifact workflow, evidence registry, and issue queue.
- `Methodology/Templates/project-workspace/`: actual project workspace templates used for the audit.
- `Methodology/Templates/section-contract.md` and `Methodology/Templates/section-dod.md`: Methodology-module templates, not part of the copyable project workspace.
