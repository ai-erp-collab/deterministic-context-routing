# Module Concept And Language


## Reader Outcome

After this section, the reader can:

- Explain a module as a business boundary, not only a folder or code package.
- Write a module concept that gives an agent the first useful business context.
- Use module language to map a human request to tables, documents, classes, settings, roles, and verification limits.
- Decide when a task belongs to the active module, a neighboring module, or project-level context.
- Recognize why a module concept can help the agent challenge unclear or defective business logic.

## Core Explanation

The previous sections define why context must be bounded, how memory layers work, and which workspace files make those layers operational. The next question is: what is the first durable business context an agent should read after it knows the active module?

That context is the module concept.

In this methodology, an ERP project is the full product workspace: global settings, shared platform behavior, reusable contracts, source evidence, and many business areas. A module is a bounded business area inside that project. Budgeting, procurement, approvals, payroll, inventory, and reporting can each be modules when they have their own vocabulary, rules, tables, documents, workflows, and responsibility boundaries.

A module is not merely a directory. It is a business responsibility boundary. The directory tells the agent where files live. The module concept tells the agent what the area means.

The module concept is the semantic interface between user intent and technical implementation. It lets a user say, "the user from a leaf department should see the parent budget unit," while the agent maps that sentence to:

- business terms such as user, leaf department, parent budget unit, and visibility;
- module boundaries such as budget access versus global organization structure;
- technical objects such as tables, documents, classes, settings, user groups, roles, statuses, UI actions, and source examples;
- existing wiki pages and contracts;
- verification limits such as runtime data, permissions setup, or configuration that cannot be checked statically.

This matters because natural-language requests usually start with business vocabulary, not file names. If the workspace only gives the agent source roots, the agent can search text but may miss the meaning. If the workspace gives the agent a module concept, the agent can reason about the request before touching code.

A strong module concept includes:

- purpose: the business problem the module solves;
- boundaries: what the module owns, what belongs to project-level context, and what belongs to neighboring modules;
- baseline capabilities: scenarios the module must always support;
- non-capabilities: what the module intentionally does not do;
- constraints: platform, runtime, data, rights, workflow, UI, or reporting limits;
- invariants: facts that must remain true after any change;
- primary entities: documents, directories, rows, settings, users, roles, statuses, and business objects;
- extension points: tables, methods, formulas, workflow states, UI actions, and configuration points;
- dependencies: shared platform behavior and neighboring modules;
- terminology dictionary: natural names, synonyms, abbreviations, multilingual variants, and legacy names;
- intent patterns: common user requests and their likely technical meaning;
- ambiguity rules: terms that require clarification before implementation;
- boundary language: requests that sound plausible but exceed the module's responsibility.

The module concept should be written in business language first. Technical links are still necessary, but they come after the concept gives them meaning. A table name without business meaning is only a string. A business term without technical anchors is only an intention. The module concept connects both sides.

Every non-trivial feature should either use the module concept or update it. If a task discovers a new invariant, synonym, role, status rule, boundary, or dependency, that discovery belongs in module memory. Otherwise the next agent will repeat the same interpretation work.

## Reproducible Procedure

1. Resolve the active module.
   - Use the workspace module registry, aliases, or latest session state.
   - If the module is unclear, ask for the module before doing non-trivial work.

2. Write the module purpose in business language.
   - State why the module exists.
   - Avoid starting with table names or class names.
   - Keep the purpose understandable to a business user.

3. Define ownership boundaries.
   - List what the module owns.
   - List what belongs to project-level or shared context.
   - List neighboring modules that the module depends on or interacts with.

4. Build the module vocabulary.
   - Record primary terms, synonyms, abbreviations, and multilingual variants.
   - Map each important term to known technical objects when that mapping exists.
   - Mark unknown mappings as open questions instead of guessing.

5. Record core entities and extension points.
   - Name important documents, directories, tables, settings, statuses, roles, groups, methods, UI actions, formulas, and workflow states.
   - Link to existing wiki pages, contract pages, source examples, or artifact indexes.

6. Capture invariants and constraints.
   - Write rules that must remain true across changes.
   - Distinguish business invariants from technical constraints.
   - Mark runtime-only constraints explicitly when they cannot be confirmed statically.

7. Add intent patterns.
   - Record common user request shapes.
   - For each pattern, name likely terms, technical objects, and verification needs.
   - Include ambiguity rules when a phrase can mean more than one thing.

8. Use the module concept during agentic workflow intake.
   - Start from the user's words.
   - Map words to module terms.
   - Map terms to technical objects.
   - Identify missing evidence, ambiguity, and runtime assumptions.

9. Update the module concept after meaningful discoveries.
   - Add new terms, mappings, boundaries, invariants, and open questions.
   - Keep detailed evidence in the appropriate wiki, contract, table, or usage page.
   - Keep the module concept as an entry point, not a raw evidence dump.

## Required Artifacts

- Module concept page in the active module wiki.
- Module purpose and boundaries.
- Module terminology dictionary.
- List of primary entities and technical anchors.
- Module invariants and constraints.
- Intent patterns and ambiguity rules.
- Links to related table pages, contract pages, usage pages, source examples, artifact indexes, and open questions.
- Session-state note when the active task changes the module concept.

## Example

A user says: "the user from a leaf department should see the parent budget unit."

Without a module concept, the agent may search for `leaf`, `department`, or `parent` and find scattered code. That may produce a local edit, but it does not prove the request was understood.

With a module concept, the agent first maps the request:

- likely module: budgeting or budget access;
- business terms: user, leaf department, parent budget unit, visibility;
- possible project-level dependency: organization hierarchy;
- possible module-level objects: budget hierarchy, access rules, budget unit tables, user group relations, access helper classes;
- ambiguity: "see" may mean list visibility, document access, report scope, selector filtering, or permission inheritance;
- runtime assumptions: actual hierarchy records, active dates, and user permissions may require runtime validation.

The agent can now ask a focused question if "see" is ambiguous, inspect the smallest relevant wiki and source evidence, and avoid treating the request as a generic UI filtering task. It can also notice a business-logic defect if the request mixes organizational department hierarchy with budget hierarchy in a way the module concept says is not always equivalent.

## Failure Modes

- Treating the module as a folder: the agent finds files but misses business responsibility.
- Starting from code names: the module concept becomes unreadable to business users and weak for task intake.
- Omitting boundaries: module-specific behavior is confused with project-level or neighboring-module behavior.
- Omitting synonyms: the agent cannot connect user vocabulary to existing technical names.
- Recording only entities and no invariants: future changes preserve structure but break business rules.
- Treating inferred mappings as confirmed: a plausible term-to-table relation becomes a false contract.
- Letting the module concept become a raw dump: the entry point becomes too expensive to read.
- Failing to update the concept after a task: durable language remains behind actual module understanding.

## Assumptions And Runtime Limits

- A module concept may start partial. Partial is acceptable when open questions and uncertainty are explicit.
- Some mappings from business terms to technical objects require source evidence or runtime observation.
- A module concept does not replace table, contract, or usage pages. It points to them.
- The method assumes the agent can read the module concept before workflow intake.

## Related Notes

- `01-why-this-method-exists.md`: explains the necessary-and-sufficient context goal.
- `02-knowledge-system.md`: defines module memory and shared memory.
- `03-workspace-bootstrap.md`: defines the module registry and wiki roots that host module concepts.
- `05-knowledge-acquisition.md`: explains how missing module knowledge is collected and classified.
- `09-agentic-workflow-with-superpowers.md`: downstream section for applying module language to a concrete request through a disciplined agent workflow.
- `Methodology/Wiki/insights.md`: records the module concept as the semantic interface for natural-language tasks.
