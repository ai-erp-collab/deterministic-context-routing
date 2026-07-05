# Why This Method Exists


## Reader Outcome

After this section, the reader can:

- Explain why proprietary ERP development is a knowledge problem before it is a coding problem.
- Explain why an agent cannot be given the whole project context for every task.
- Name the method's central goal: provide the necessary and sufficient context for the current task.
- Understand why later sections define memory layers, workspace files, module concepts, and verification rules.

## Core Explanation

In ordinary software work, an agent can often rely on public ecosystem knowledge: common frameworks, public APIs, compiler behavior, package documentation, examples, and searchable error messages. Proprietary ERP work is different.

In IT-Enterprise and similar systems, important behavior is distributed across closed platform libraries, project libraries, table schemas, document types, settings, UI actions, workflow states, formulas, user groups, runtime conventions, and business vocabulary. Some libraries may be unavailable as public documentation. Some behavior cannot be checked with a normal local compiler. Some contracts are visible only through source examples, exported schemas, user documentation, or runtime observations. The agent does not arrive knowing these internals.

That creates a context-management problem. The workspace may contain a huge amount of useful material: source examples, platform contracts, table exports, wiki pages, plans, review notes, and session history. Putting all of it into the agent's prompt is not viable. The context window is limited, token cost matters, and excessive context can be as harmful as missing context because it buries the few facts that matter.

The method exists to solve that problem. Its main task is to give the agent the necessary and sufficient context for the current task:

- necessary: the agent has the domain terms, contracts, files, assumptions, and examples needed to act safely;
- sufficient: the agent has enough evidence to decide, implement, document, and verify without guessing;
- bounded: unrelated history, broad source dumps, and stale facts stay outside the active context.

This is why the methodology treats documentation as part of engineering. A wiki page, module concept, section contract, artifact index, or session-state entry is not paperwork. It is routing infrastructure that helps future agents load the right context cheaply.

When the agent receives enough business context, it can do more than generate code. It can challenge the task wording, notice contradictions in business rules, point to missing cases, and sometimes find defects in the requested business logic before implementation starts. That only works when the project gives the agent the module idea, purpose, boundaries, terms, and evidence needed to reason in the business domain instead of only manipulating files.

The rest of the method follows from this premise. First define the memory model. Then create workspace files that make the memory model operational. Then use module concepts, table contracts, class contracts, usage flows, plans, implementation notes, and verification records to keep each task inside a useful context boundary. In short: build deterministic context routing instead of relying on broad search, raw dumps, or chat memory.

## Reproducible Procedure

1. Start every methodology or feature task by naming the context problem.
   - What part of the proprietary ERP is opaque to the agent?
   - Which behavior is hidden in platform conventions, tables, configuration, or runtime state?
   - Which facts are needed for this task, and which facts are noise?

2. Separate evidence from active context.
   - Evidence can be large: source material, exports, historical notes, and examples.
   - Active context must be small: the exact terms, contracts, assumptions, and files needed now.

3. Convert repeated discoveries into durable memory.
   - A fact needed once can remain in a task note.
   - A fact needed again belongs in wiki, a contract page, a module concept, or a known issue.

4. Preserve uncertainty.
   - If behavior cannot be verified in the target runtime, mark it as an assumption or runtime limit.
   - Do not let the agent convert an inference into a confirmed rule.

5. Check whether the current task has necessary and sufficient context before implementation.
   - If not enough context exists, acquire or document it first.
   - If too much context is loaded, narrow the task and use curated wiki pages instead of raw dumps.

## Required Artifacts

- A statement of the active module or product area.
- The module idea and purpose, written in business language.
- The module boundaries: what this module owns, what belongs to the wider ERP project, and what belongs to neighboring modules.
- A short list of required domain terms and technical objects.
- Links to the smallest relevant wiki, source, artifact, design, or session notes.
- Explicit runtime assumptions when behavior cannot be verified directly.
- A place to store durable discoveries after the task.

## Example

A user says: "the user from a leaf department should see the parent budget unit."

The agent should not load every budget source file and every table export. It should first identify the necessary context:

- business terms: user, leaf department, parent budget unit, visibility;
- likely module: budget-related module;
- likely evidence: module concept, organization hierarchy notes, budget hierarchy tables, access-rule usage flow, relevant helper contracts;
- runtime limits: whether visibility can be tested in the target ERP session.

If those facts are already curated, the agent reads the wiki pages and a small number of source references. If they are not curated, the task includes knowledge acquisition before implementation. The goal is not maximal context. The goal is the smallest context that makes the change safe.

## Failure Modes

- Treating proprietary ERP work as ordinary code completion: the agent misses table, configuration, workflow, or runtime contracts.
- Loading everything: the context window fills with broad source material and the important facts become harder to find.
- Loading too little: the agent implements from natural language without domain mapping.
- Trusting public or generic framework knowledge: closed platform behavior is assumed instead of verified.
- Hiding uncertainty: static evidence is presented as runtime-confirmed behavior.
- Keeping discoveries only in chat: the next task repeats the same investigation.

## Assumptions And Runtime Limits

- The method assumes the agent can read local project files and curated notes.
- The method does not assume access to a full proprietary runtime or a normal compiler.
- Some evidence will remain partial. Partial evidence is useful only when its limits are explicit.
- The method optimizes for useful context, not exhaustive context.

## Related Notes

- `02-knowledge-system.md`: explains the memory layers used to manage context.
- `03-workspace-bootstrap.md`: explains how to create files and folders that make the memory model operational.
- `04-module-concept-and-language.md`: explains the module concept as the language bridge between user intent and technical objects.
- `Methodology/Wiki/insights.md`: records necessary-and-sufficient context as a core insight.
