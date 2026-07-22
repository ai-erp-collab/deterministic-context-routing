# Adoption Bootstrap And Template Audit


## Reader Outcome

After this section, the reader can:

- Bootstrap the methodology in another project without relying on chat history.
- Decide what to copy, what to adapt, and what to mark project-specific.
- Run the first module setup, first curation pass, and first workflow-backed task.
- Audit the guide against the starter templates.
- Identify claims in the guide that are unsupported by actual template artifacts.

## Core Explanation

Adoption should end with a usable workspace, not only agreement with the method.

The safest path is incremental: start from a project or module idea, create the starter structure, register one module, write one module concept, normalize one small artifact or source contract, run one workflow-backed task, update documentation, and then audit the template package. This proves that the guide is executable and that its examples are grounded in real files.

The audit is part of the method. It catches two kinds of drift:

- the guide promises an artifact that the starter kit does not provide;
- the starter kit contains a template or rule that the guide never explains.

It also separates universal guidance from project-specific examples. Encoding rules, SQL dialect details, proprietary runtime constraints, source roots, table parsers, build limitations, compiler availability, version-control availability, and runtime access should be labeled as project requirements, not sold as universal methodology.

## Bootstrap Procedure

1. Create the starter workspace.
   - Add root instructions, root idea, known issues, module registry, root session state, docs folders, knowledge roots, source artifact roots, and one module folder.
   - Copy only the universal parts of the instruction templates.

2. Write the project idea.
   - State why the workspace exists, who it serves, which business areas are in scope, which first modules are expected, what evidence is available, and which open questions shape the first dialogue.
   - Treat this as one-time bootstrap input. After the first artifacts exist, durable meaning belongs in the module registry, module concept, wiki pages, plans, and session state.

3. Add project-specific rules.
   - Record a capability profile for Git, compiler/build, automated tests, runtime access, static checks, encoding, SQL/runtime, source access, privacy, deployment, and other tooling constraints.
   - Mark them as project-specific.
   - Add required verification commands when the project has them.
   - Keep session-state updates mandatory even in Git-enabled projects because commits and logs are not reliable task-continuity memory.

4. Register the first module.
   - Add canonical name, aliases, module path, wiki root, shared wiki root, source roots, artifact roots.
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
- `session/session-state-entry.md`.

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
- `section-contract.md`: project-specific to this Methodology module's section-writing workflow.
- `section-dod.md`: project-specific to this Methodology module's section quality gate.

### Project-Specific Material

When publishing the guide, mark these as project examples unless they are true for the target project:

- absence of git;
- absence of local compiler or build verification;
- UTF-8 and Cyrillic encoding scan;
- exact artifact paths such as `source-artifacts/tables/raw`;
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
5. Import one table export into raw artifacts.
6. Use the curator workflow to create one table contract and update the artifact index.
7. Document one access or posting usage flow.
8. Run one small feature or documentation task through the workflow.
9. Update session state.
10. Run the template audit.

This proves the process on a narrow slice before scaling it across modules.

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

## Assumptions And Runtime Limits

- Adoption is iterative; the first version can be partial if uncertainty is explicit.
- The target project may have different runtime, source access, encoding, or verification constraints.
- The target project may have Git, a compiler, automated tests, or runtime access; when present, those capabilities should strengthen verification but not replace session state.
- A starter kit should prefer small templates and real examples over broad claims.
- The audit checks consistency, not correctness of business behavior.

## Related Notes

- `04-workspace-bootstrap.md`: conceptual bootstrap background.
- `10-agentic-workflow-with-superpowers.md`: recommended workflow boundary.
- `12-practical-workspace-template.md`: practical starter workspace template.
- `13-kb-curator-and-artifact-workflow.md`: curator and artifact workflow.
- `Methodology/Templates/project-workspace/`: actual project workspace templates used for the audit.
- `Methodology/Templates/section-contract.md` and `Methodology/Templates/section-dod.md`: Methodology-module templates, not part of the copyable project workspace.
