# Practical Workspace Template


## Reader Outcome

After this section, the reader can:

- Create a minimal file-based workspace that an agent can navigate.
- Separate universal starter rules from project-specific rules.
- Define a project capability profile for Git, compiler, test, runtime, and static-check availability.
- Use project and module `idea.md` files as one-time bootstrap inputs.
- Write root and module instruction files without inventing unsupported process.
- Register modules, wiki roots, source roots, and artifact roots.
- Add the templates needed for first module concepts, table contracts, class contracts, usage flows, designs, plans, and session notes.
- Add confidence labels to important wiki and contract claims.

## Core Explanation

The practical starting point is not a theory of documentation layers. It is a workspace that tells the agent where to start, what to read, what to avoid over-reading, where durable knowledge belongs, and what must be verified before work is called finished. The workspace is a deterministic context-routing system, not a documentation archive.

The starter template should be copied from real working artifacts whenever possible. Universal pieces can be reused almost as-is. Project-specific pieces should be clearly marked as examples, not rules for every team. In this project, encoding checks, absence of git, absent compiler/runtime verification, table export folders, and module aliases are project-specific. The pattern of having these rules is universal; the exact rules are not.

A useful starter workspace has four jobs:

- orientation: resolve active module and local rules;
- memory: preserve compact restart context and durable knowledge;
- evidence: keep raw and processed source artifacts auditable;
- confidence: label important claims as confirmed, inferred, runtime-unverified, or blocked-by-access;
- workflow integration: give Superpowers or an equivalent workflow enough project context to plan, implement, verify, and update documentation.

## Starter Structure

Use this as the minimal shape, then adapt paths to the project:

```text
workspace/
  AGENTS.md
  idea.md        # bootstrap input, not recurring memory
  known_issues.md
  modules.md
  session_state.md
  docs/
    superpowers/
      specs/
      plans/
  knowledge-base/
    INDEX.md
    shared/
    modules/
      <module>/
  source-artifacts/
    INDEX.md
    tables/
      raw/
      processed/
  <module>/
    AGENTS.md
    idea.md      # bootstrap input, not recurring memory
    session_state.md
    docs/
```

For a documentation-only methodology module, this project also uses:

```text
Methodology/
  AGENTS.md
  Methodology/
    sections/
  Templates/
  Wiki/
  Assembly/
  Output/
  session_state.md
```

That second shape is project-specific. It is useful when the documentation itself is the product and must be assembled from source sections.

## Root Instructions Template

Root `AGENTS.md` should define universal behavior first:

```markdown
# Workspace Rules

- Read `known_issues.md` before non-trivial work.
- Read `modules.md` to resolve module names, aliases, paths, wiki roots, source roots, and artifact roots.
- If the active module is unclear, ask which module to use.
- If no module is explicitly requested, continue with the last active module named in root `session_state.md`.
- Read the active module `AGENTS.md` before non-trivial work.
- Read only the latest entry in the active module `session_state.md`: stop at `<!-- AGENT-SESSION-STOP -->`.
- Keep module-specific durable knowledge in the module wiki.
- Keep reusable platform or cross-module knowledge in shared knowledge.
- Keep raw source artifacts separate from curated knowledge.
- Update the active module `session_state.md` after every non-conversational task.
- Update root `session_state.md` only as a compact module activity index.
- When full automated testing is impossible, document static checks and remaining runtime assumptions.
- Keep `session_state.md` even when Git exists; Git records file history, while session state records task intent, evidence, assumptions, verification, and next action.
```

The root `idea.md` is not part of the recurring reading path. Use it as a one-time bootstrap input: a user can say, "Here is the project idea; read it, ask questions if anything is unclear, and create the needed starter artifacts." After bootstrap, the durable meaning should live in `modules.md`, module instructions, module concept pages, plans, and session notes.

The root `session_state.md` should stay compact. Its job is to say which module was active most recently and to index recent module-level work, not to preserve every detail. A good entry names the module, the durable pages or artifacts touched, the verification performed, and the next useful action. Durable facts should move into module or shared knowledge, with `session_state.md` linking to them.

Then add project-specific rules in the same file, clearly marked:

```markdown
## Project-Specific Rules

- Capability profile:
  - Git: unavailable. Use filesystem/static verification instead of `git status` or `git diff`.
  - Compiler/build: unavailable. Use syntax-aware static scans where possible and record remaining assumptions.
  - Automated tests: unavailable or incomplete. Name any manual or static checks used.
  - Runtime access: unavailable locally. Mark behavior that depends on target runtime settings as runtime-unverified.
- Example: Preserve UTF-8 for Cyrillic text and run the project's encoding scan after Markdown/source edits.
- Example: Use the project's table artifact folders for XML/CSV/TXT exports.
- Example: Use the project's wiki curator skill or script when normalizing source evidence.
```

The examples above come from this project and represent the hard-case baseline. Another project may replace them with SQL dialect rules, build-system limits, deployment constraints, data privacy rules, or runtime access rules. If Git exists, define how to use local status, diffs, and recent history. If a compiler, build command, test runner, or local runtime exists, define the exact commands and make them part of the verification rule. Do not remove `session_state.md`: Git history, build logs, and test output do not reliably preserve why a task happened, what evidence was used, which assumptions remain, or what should happen next.

## Module Instructions Template

Each module should have a smaller `AGENTS.md`:

```markdown
# <Module> Module Rules

- Read `../AGENTS.md` first.
- Read `../known_issues.md` before non-trivial work.
- Read `../modules.md` to resolve module paths.
- Module: <Module>.
- Module wiki lives in `<module-wiki-root>/`.
- Supporting docs, specs, and plans live in `<module>/docs/`.
- Work on one task or section at a time.
- Update `session_state.md` after every non-conversational module task.
- Preserve project encoding and verification rules.
```

Then add module-specific rules:

```markdown
## Module-Specific Rules

- Example: This module is documentation-only.
- Example: Source sections live in `Methodology/sections/`.
- Example: Final assembled output must not be edited directly except during mechanical assembly.
- Example: Avoid project-sensitive source-origin wording; use neutral evidence names.
```

Again, these examples are from this project. The universal part is the structure: module rules inherit root rules, identify the module, name the local knowledge roots, and record module-specific constraints.

The module `idea.md` has the same one-time role as the project idea. Use it when the user asks the agent to bootstrap a module from an idea file or idea text. Once the module concept and initial routing artifacts exist, agents should normally read the module wiki and session state instead of re-reading the original idea.

The module `session_state.md` is more detailed than the root one, but it is still short memory. It should contain only the latest restart context before the stop marker: current task or section, source material used, decisions, open questions, verification, and next action. Older history can remain below the marker for audit purposes, but agents should not treat it as current instruction.

## Module Registry Template

`modules.md` should be short and mechanical:

```markdown
# Modules

- <ModuleName>
  - path: `<module-path>/`
  - wiki: `<module-wiki-root>/`
  - shared wiki: `<shared-wiki-root>/`
  - sources: `<source-root>/`, `<example-source-root>/`
  - artifacts: `<artifact-root>/`
  - aliases: <natural language aliases>
```

This is the file that turns natural language into paths. Keep aliases practical: names users actually type, abbreviations, and domain nicknames.

## Required Templates

At minimum, create templates for:

- module concept page;
- table page;
- class or function contract page;
- usage flow page;
- design doc;
- implementation plan;
- session-state entry.

Wiki and contract templates should separate page status from claim confidence. `status` says whether the page is complete enough for use. `confidence` says how a specific fact is supported: `confirmed`, `inferred`, `runtime-unverified`, or `blocked-by-access`.

Project and module `idea.md` files are recommended bootstrap inputs, especially for new workspaces. They are not recurring operational artifacts, and mature modules may not need retroactive idea files if their intent is already captured in durable wiki pages and plans.

This project stores the copyable project-workspace templates in `Methodology/Templates/project-workspace/templates/`. Another project can store them under root `templates/` or a module docs folder, but the templates should be easy for agents to find.

This project also ships a copyable project workspace package in `Methodology/Templates/project-workspace/`. It contains root and module `idea.md` files, root starter files, one example module, knowledge roots, source artifact folders, workflow folders, and reusable page templates grouped into `wiki`, `workflow`, and `session` template folders. Treat it as a starting point to adapt, not as a finished project configuration.

The root of `Methodology/Templates/` is reserved for templates used to produce this methodology itself, such as `section-contract.md` and `section-dod.md`. Those are product-specific templates for writing this book from section files. They are not required for every ERP project unless that project also produces assembled documentation from source sections.

## Reproducible Procedure

1. Create the root structure.
   - Add root instructions, root idea, known issues, module registry, root session state, docs, shared knowledge, module knowledge, source artifacts, and at least one module folder.

2. Write the project idea.
   - Capture project purpose, audience, business scope, initial modules, available evidence, workflow expectations, open questions, and the first useful next step.
   - Keep it short enough to start a dialogue, not to replace later designs or plans.
   - Treat it as input to the bootstrap conversation, not as a file every agent must read forever.

3. Add root instructions.
   - Start from the universal template.
   - Add a clearly marked project-specific section.
   - Include a capability profile for Git, compiler/build, automated tests, runtime access, static checks, and runtime-assumption rules.

4. Add the first module.
   - Create module idea, module instructions, and module session state.
   - Register the module in `modules.md`.
   - Create the module wiki root or point to the module's established wiki location.

5. Write the module idea.
   - Capture module purpose, users and actors, business capabilities, boundaries, core terms, common starting requests, first evidence, open questions, and next action.
   - Use it as the source for the first module concept page.
   - For mature existing modules, skip the retroactive idea file when the same intent already lives in curated module knowledge.

6. Add session-state templates.
   - Create a compact root entry template for last active module, recent durable changes, verification, and next action.
   - Create a module entry template for current task or section, source material, decisions, open questions, verification, and next action.
   - Include the stop marker rule for module histories that accumulate entries.

7. Add starter templates.
   - Create module concept, table, contract, usage flow, design, plan, and session-state templates.
   - Keep templates short enough to be reused, not polished into prose essays.

8. Add artifact lifecycle folders.
   - Create raw and processed source artifact areas.
   - Create an artifact index.
   - State when raw artifacts may move to processed.

9. Add project-specific guardrails.
   - Encoding rules, SQL/runtime constraints, proprietary access limits, build/test limits, privacy rules, available tooling, or absent tooling belong here.
   - Mark them as examples when publishing a generic guide.

10. Run a template audit before calling the starter kit complete.
   - Check that every template mentioned in the guide exists.
   - Check that every shipped template is explained in the guide.
   - Check that project-specific rules are not presented as universal.

## Required Artifacts

- Root `AGENTS.md`.
- `known_issues.md`.
- `modules.md`.
- Root `session_state.md`.
- At least one module `AGENTS.md`.
- At least one module `session_state.md`.
- Shared and module knowledge roots.
- Raw and processed source artifact roots plus artifact index.
- Starter page templates.
- Copyable starter workspace package when publishing the methodology.
- Verification or guardrail scripts when the project requires them.

Recommended bootstrap artifacts:

- Root `idea.md` for a new project.
- Module `idea.md` for a new module.

Optional artifacts:

- Pattern page template or pattern folder, when reusable patterns become common enough to justify a separate page family.

## Example

In this project, the root instructions contain universal routing rules and project-specific rules. Universal rules include reading `modules.md`, resolving the active module, reading only the latest module session entry, keeping session state even if a version-control system exists, and writing durable knowledge to the module or shared wiki. Project-specific rules include the absence of git, absence of local compiler/runtime verification, the encoding scan for Cyrillic-sensitive changes, and the table artifact lifecycle.

The same routing idea applies inside pages. A module concept should route from user language to tables, contracts, and flows. A table page should route from business terms to fields, evidence, and usage. A contract page should route from API names to behavior, side effects, and verification gaps. A usage flow should route from a scenario to the affected contracts, tables, checks, and remaining uncertainty.

The Methodology module then adds local rules: it is documentation-only, source sections live under `Methodology/sections/`, templates live under `Templates/`, final output lives under `Output/`, and output should not be edited directly except during mechanical assembly.

A new adopter project would start one level earlier: root `idea.md` states why the workspace exists and which first modules matter; the first module `idea.md` states the module's business purpose and starting requests. The module concept then turns that initial intent into durable module memory with terms, boundaries, intent patterns, links, and invariants. Existing mature modules can skip retroactive `idea.md` creation when their intent already lives in curated knowledge.

Root `session_state.md` says Methodology was the last active module and summarizes recent module activity. `Methodology/session_state.md` carries the restart context for the current documentation work: which sections changed, which checks passed, and which next action remains. Neither file is the durable home for the methodology rules; the source sections, wiki pages, and templates are.

That split is the pattern to copy: keep the routing structure universal, and label the project constraints honestly.

## Failure Modes

- Publishing project-specific rules as if every project must use them.
- Starting with a large wiki before the agent has routing instructions.
- Writing pages that explain a topic but do not route to related contracts, artifacts, confidence labels, or verification gaps.
- Omitting module aliases, causing natural-language requests to miss the right path.
- Skipping explicit starting intent, causing the first dialogue to start from files instead of business purpose.
- Keeping raw exports in the wiki instead of source artifact folders.
- Shipping templates that the guide never explains.
- Explaining artifacts in the guide that do not exist in the starter kit.
- Copying the starter workspace without replacing placeholders and project-specific examples.
- Treating assembled output as the editable source.
- Letting `session_state.md` become a hidden wiki instead of a restart note and activity index.
- Treating Git history, build logs, or test output as a replacement for session state.
- Failing to enable stronger verification when Git, compiler/build, tests, or runtime access are available.

## Assumptions And Runtime Limits

- This template assumes a file-based workspace where agents can read and update Markdown files.
- Folder names can change, but responsibilities should remain explicit.
- Some projects may need stronger access-control, privacy, or runtime rules than this starter kit shows.
- Encoding guardrails, unavailable git, unavailable compiler/build checks, test coverage, and runtime access limits are project-specific constraints, not universal assumptions.

## Related Notes

- `02-knowledge-system.md`: explains why memory needs layers.
- `03-workspace-bootstrap.md`: explains the earlier conceptual bootstrap.
- `09-agentic-workflow-with-superpowers.md`: explains the workflow integration boundary.
- `11-kb-curator-and-artifact-workflow.md`: downstream section for curator and artifact practice.
- `12-adoption-bootstrap-and-template-audit.md`: downstream section for adoption and template audit.
