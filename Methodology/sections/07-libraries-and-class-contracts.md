# Libraries And Class Contracts


## Reader Outcome

After this section, the reader can:

- Explain why class and method documentation should describe behavior, not merely syntax.
- Decide when a library, class, function, or method deserves a contract page.
- Write a contract page with purpose, API shape, inputs, outputs, side effects, errors, dependencies, and examples.
- Link behavior contracts to affected tables, usage flows, module terms, and runtime assumptions.
- Avoid copying large code bodies into curated memory.

## Core Explanation

Tables describe important parts of system state. Libraries and classes describe behavior that reads, changes, validates, displays, or interprets that state.

A source file is evidence. A class contract is curated memory. The source file shows how behavior is implemented at a point in time. The contract states what future users of that behavior may rely on: what the class is for, how it should be called, what it reads or writes, what errors it can raise, which runtime conditions it depends on, and which tables or workflows it affects.

This distinction is important in proprietary ERP work because behavior is often distributed across project libraries, platform libraries, UI actions, table contracts, workflow states, formulas, settings, and runtime conventions. A method signature alone is not enough. A future agent needs to know whether the method writes persistent data, depends on prepared temp tables, checks permissions, changes statuses, displays messages, calls UI behavior, evaluates formulas, or assumes specific configuration.

A contract page should be created or refreshed when a code unit is reusable, externally called, module-defining, risky, or hard to infer from local code. Private helpers do not always need contract pages. But a private helper can still deserve documentation if it expresses an important module rule. In that case, it may belong in a usage page or module concept instead of being presented as a stable public API.

The contract page is also a context-routing entry point. It should summarize behavior and link to source evidence, table pages, usage flows, and examples. It should not copy large code bodies. The goal is to let future work understand the behavioral contract before deciding whether deeper source reading is needed.

Platform libraries follow the evidence rule from knowledge acquisition: inspect or document them only when access exists and license or project rules allow that use. If the likely behavior is hidden behind a restricted source, mark the gap as blocked-by-access or runtime-unverified instead of inventing confidence.

## Reproducible Procedure

1. Decide whether the code unit needs a contract.
   - Create a contract for reusable APIs, module boundaries, shared helpers, public services, and methods with persistent side effects.
   - Consider a contract when the code affects tables, permissions, statuses, UI behavior, formulas, workflow, or runtime setup.
   - Prefer usage or module pages for private helpers that express business rules but are not stable APIs.

2. Locate permitted evidence.
   - Check existing contract pages and usage pages first.
   - Inspect project libraries and source examples when they are part of the workspace.
   - Inspect platform libraries only when access exists and license or project rules allow that use.
   - Use table pages, module concept pages, user documentation, and runtime observations to interpret behavior.

3. State the contract purpose.
   - Describe the business or technical responsibility in one or two paragraphs.
   - Name the module terms the contract supports.
   - State non-goals when misuse is likely.

4. Document the public shape.
   - Record class, function, or method name.
   - Record signature, parameters, return values, and expected input state.
   - Record default behavior and important options.
   - Avoid implementation detail unless callers must know it.

5. Document behavioral effects.
   - List tables read or written.
   - List status changes, messages, UI calls, permission checks, formula evaluation, workflow transitions, temp-table assumptions, and external dependencies.
   - State whether persistent side effects are absent when that fact matters.

6. Document errors and limits.
   - List exceptions, user-visible messages, validation failures, and unsupported cases when known.
   - Mark runtime assumptions, partial evidence, inferred behavior, and blocked-by-access gaps.

7. Add examples of correct use.
   - Prefer small examples that show inputs, expected output, and side effects.
   - Link to source examples instead of copying large code.
   - Include counterexamples only when they prevent common misuse.

8. Link the contract into the knowledge system.
   - Link affected table pages.
   - Link usage flows that compose this contract with other contracts.
   - Link module concept terms and open questions.
   - Add or update indexes so the contract is discoverable.

## Required Artifacts

- Contract page for the library, class, function, or method.
- Links to permitted source evidence.
- Links to affected table pages or an explicit note that no persistent table side effects are known.
- Inputs, outputs, side effects, errors, dependencies, examples, and confidence labels.
- Open questions for runtime behavior, restricted sources, or unclear callers.
- Index or related-notes updates that make the contract discoverable.

## Example

A budgeting access class determines which budget context a user can see.

A weak contract page would only list the class name and method signatures. A useful contract page answers:

- what business responsibility the class owns;
- which module terms it implements, such as user department, budget unit, access scope, and parent unit;
- which tables or table contracts it reads;
- whether it writes data or only computes visibility;
- which permissions, hierarchy records, active dates, or runtime settings it assumes;
- what happens when setup is missing;
- which usage flow demonstrates correct use;
- which behavior is confirmed by source evidence and which remains runtime-unverified.

With that contract, a future task can reason about access behavior without rereading the entire implementation first.

## Failure Modes

- Documenting only syntax: the signature is known, but the behavior is still opaque.
- Copying large code bodies: the contract becomes expensive to read and quickly goes stale.
- Omitting side effects: callers miss database writes, status changes, UI calls, or messages.
- Omitting table links: behavior is disconnected from the data contracts it relies on.
- Treating private helpers as stable public APIs.
- Hiding runtime assumptions: behavior appears confirmed even though data, configuration, or permissions were not checked.
- Ignoring access and license limits for platform libraries.
- Updating code without updating a changed public contract.

## Assumptions And Runtime Limits

- A contract page can be partial when uncertainty is explicit.
- Static source evidence can describe code paths, but not every runtime data or configuration case.
- Platform-library behavior can be documented only from permitted evidence.
- A contract page is not a substitute for source review when implementation details matter; it is the entry point that tells the agent whether deeper reading is needed.

## Related Notes

- `05-knowledge-acquisition.md`: defines permitted evidence and confidence labels.
- `06-tables-as-contracts.md`: explains the data contracts that behavior often relies on.
- `08-usage-flows-and-patterns.md`: downstream section for composing contracts into business scenarios.
- `09-agentic-workflow-with-superpowers.md`: downstream section for mapping user requests to affected contracts through a disciplined agent workflow.
- `10-practical-workspace-template.md`: downstream section for placing contracts in a practical starter workspace.
