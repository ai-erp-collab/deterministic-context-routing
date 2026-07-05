# Preface


## Reader Outcome

After this section, the reader can:

- Decide whether to read the full methodology or jump to the practical starter sections.
- Name the practical benefits of the method.
- Understand that the method is useful beyond proprietary ERP, even though proprietary ERP is the source environment.
- Use the table of contents as a reading path.

## What This Method Gives You

This methodology is a practical way to work with large, under-documented, domain-heavy software projects without letting quality decay as context grows.

It was developed in proprietary ERP work, where the hard part is rarely only writing code. The hard part is knowing which tables, platform conventions, project libraries, business terms, runtime assumptions, and historical decisions matter for the current task. Public documentation may be incomplete or unavailable. Runtime checks may be expensive or impossible locally. The agent can help only if the project gives it the right context without flooding it with everything.

The method turns that problem into deterministic context routing: `modules.md` routes the request to a module, the module concept translates business language into technical anchors, wiki pages and contracts provide compact durable knowledge, artifact indexes preserve evidence, and session state carries restart context. Each artifact exists to make future work cheaper and safer.

The practical benefits are:

- work on large projects without losing the thread between tasks;
- make proprietary or poorly documented systems understandable to an agent;
- apply the same pattern to any project where knowledge is too large to load all at once;
- reduce token use by routing the agent to small, curated pages instead of raw source dumps;
- preserve quality while working economically; the method was designed and used successfully on a minimal Codex subscription without hitting limits;
- create technical documentation as a working product of real work, not as a separate cleanup project that never happens;
- treat documentation as routing infrastructure for future agents, not as prose written after the useful work is done;
- lower dependence on chat history and individual memory;
- make agent work auditable: what evidence was used, what changed, what was verified, and what remains uncertain;
- start from an idea and end with concrete artifacts: module registry, module concept, contracts, usage flows, plans, and verification records.

## Table Of Contents

1. **Why This Method Exists**: the context-management problem and why proprietary ERP work exposes it sharply.
2. **Knowledge System**: the memory layers that keep durable knowledge separate from short task context.
3. **Workspace Bootstrap**: the root files and folders that make the method operational.
4. **Module Concept And Language**: the bridge between user intent and technical objects.
5. **Knowledge Acquisition**: how evidence becomes durable, uncertainty-aware knowledge.
6. **Tables As Contracts**: table schemas as business and data contracts.
7. **Libraries And Class Contracts**: APIs, classes, functions, and runtime assumptions as behavior contracts.
8. **Usage Flows And Patterns**: scenario pages that connect tables and contracts into working behavior.
9. **Agentic Workflow With Superpowers**: how this knowledge system integrates with design, planning, implementation, and verification workflows.
10. **Practical Workspace Template**: the starter structure, instruction files, templates, and bootstrap artifacts.
11. **KB Curator And Artifact Workflow**: the raw-to-curated-to-processed workflow for source evidence.
12. **Adoption Bootstrap And Template Audit**: how to prove the method on one module and check the guide against shipped templates.

## How To Read This

For the concept, read sections `01` through `09` in order. They explain why the method works.

For adoption, start with sections `10`, `11`, and `12`. They show the copyable workspace shape, the curator workflow, and the audit loop.

For an existing project, do not try to rewrite everything at once. Pick one module, write or identify its module concept, curate one real artifact, run one workflow-backed task, and update session state. The method becomes useful when it proves itself on a narrow slice.

## Practical Scope

The examples come from proprietary ERP development, but the pattern is broader. Any project with a large codebase, scarce documentation, domain-specific vocabulary, expensive runtime checks, or long-lived agent collaboration can use the same structure.

The goal is not to create a perfect encyclopedia. The goal is to keep exactly enough knowledge close to the task: enough to reason, implement, verify, and document without repeatedly rediscovering the same facts.

## Failure Modes

- Treating the method as documentation theater instead of deterministic context routing.
- Trying to document every system before proving the workflow on one module.
- Loading raw source material when a compact curated page would be enough.
- Keeping decisions only in chat history.
- Making every artifact mandatory instead of separating required, recommended, optional, and project-specific pieces.
- Optimizing only for token savings and losing verification quality.

## Assumptions And Runtime Limits

- The method assumes a file-based workspace that agents can read and update.
- It does not require full local runtime access, but it requires honest runtime-assumption notes when verification is incomplete.
- It works best when each task updates the smallest durable knowledge page that would make the next similar task cheaper.

## Related Notes

- `01-why-this-method-exists.md`: explains the core context problem.
- `10-practical-workspace-template.md`: gives the starter workspace shape.
- `12-adoption-bootstrap-and-template-audit.md`: gives the adoption path and template audit.
