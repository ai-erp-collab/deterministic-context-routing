# Libraries And Class Contracts


## Reader Outcome

After this section, the reader can:

- Explain why class and method documentation should describe behavior, not merely syntax.
- Decide when a library, class, function, or method deserves a contract page.
- Write a contract page with purpose, API shape, inputs, outputs, side effects, errors, dependencies, and examples.
- Link behavior contracts to affected tables, usage flows, module terms, and runtime assumptions.
- Avoid copying large code bodies into curated memory.
- Decide which module owns a rule that another module needs, and expose it through an owner API instead of copying it into the consumer.

## Core Explanation

Tables describe important parts of system state. Libraries and classes describe behavior that reads, changes, validates, displays, or interprets that state.

A source file is evidence. A class contract is curated memory. The source file shows how behavior is implemented at a point in time. The contract states what future users of that behavior may rely on: what the class is for, how it should be called, what it reads or writes, what errors it can raise, which runtime conditions it depends on, and which tables or workflows it affects.

This distinction is important in proprietary ERP work because behavior is often distributed across project libraries, platform libraries, UI actions, table contracts, workflow states, formulas, settings, and runtime conventions. A method signature alone is not enough. A future agent needs to know whether the method writes persistent data, depends on prepared temp tables, checks permissions, changes statuses, displays messages, calls UI behavior, evaluates formulas, or assumes specific configuration.

A contract page should be created or refreshed when a code unit is reusable, externally called, module-defining, risky, or hard to infer from local code. Private helpers do not always need contract pages. But a private helper can still deserve documentation if it expresses an important module rule. In that case, it may belong in a usage page or module concept instead of being presented as a stable public API.

The contract page is also a context-routing entry point. It should summarize behavior and link to source evidence, table pages, usage flows, and examples. It should not copy large code bodies. The goal is to let future work understand the behavioral contract before deciding whether deeper source reading is needed.

Platform libraries follow the evidence rule from knowledge acquisition: inspect or document them only when access exists and license or project rules allow that use. If the likely behavior is hidden behind a restricted source, mark the gap as blocked-by-access or runtime-unverified instead of inventing confidence.

### Cross-Module Rules: Owner API Instead Of Copies

A contract becomes most valuable at a module boundary. Here, a module is one entry in the workspace module registry (`modules.md`), with its own instructions and its own knowledge base. Sooner or later one module needs a rule that belongs to another: an approval module must show only the rows a user may see according to the budgeting module's hierarchy, or a document module must reuse another module's status logic.

The cheap move is to copy the rule: the recursive query over the other module's hierarchy table, its status codes, its access groups, its magic level constants. The copy works on the day it is written and then drifts. The owner module changes its hierarchy walk, its admin check, or its effective-date logic, and the copy keeps the old behavior. Two algorithms now claim to implement the same business rule, and no single page can say which one is right.

The rule of this method: if module A uses domain logic that conceptually belongs to module B, the source of truth stays in module B. In this relation, B is the **owner module** and A is the **consumer module**.

The owner module:

- exposes a small public method, or a small set of methods, named after the consumer scenario;
- implements it on top of its existing, already-checked private helpers, so no second algorithm appears;
- returns simple values (a flag, an identifier, a list of identifiers, a small data object) rather than its internal table structure;
- documents the API as a contract page in its own knowledge base and names the consumer modules that may use it.

The consumer module keeps only an **adapter**: the thin local code that calls the owner API, passes its own parameters, and applies the result in its own filter, form field, or workflow step. The consumer does not copy the owner's queries, hierarchy traversals, statuses, access groups, or constants. If such code appears in a consumer, the rule has leaked out of its owner and should be moved back behind the owner API.

To decide which module owns a rule, route through the registry rather than guessing: find the module whose subject area the rule belongs to in `modules.md`, then open its instructions and knowledge-base `INDEX.md`. If the rule is about that module's tables, hierarchy, statuses, routes, or access, that module is the owner. If the rule is reused widely but still rests on one module's domain, the API still lives in that module, and shared knowledge only links to it. Only a rule that is genuinely platform-level and belongs to no business module goes to shared knowledge itself.

The consumer list on the owner contract page is not decoration. Before the owner changes the signature, return values, or meaning of an owner API, it checks every listed consumer's adapter and usage page, because those are exactly the places the change can break. The same page keeps a short change history, so a later reader of the owner module can see which consumer caused each change and why.

How a task in one module is allowed to reach into another, how the owner is looked up, and how the owner module learns that it was changed belong to the agent workflow, not to the contract itself; `10-agentic-workflow-with-superpowers.md` describes that procedure.

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

9. When another module needs the behavior, expose it through an owner API.
   - Reach into the owner module only through the cross-module procedure in `10-agentic-workflow-with-superpowers.md`, which also defines the lookup order and the mark left in the owner.
   - Determine the owner module through the module registry, as described in the core explanation.
   - In the owner module, find the existing helper where the logic already lives.
   - Add a public method named after the consumer scenario that reuses the existing private helpers and returns simple values.
   - In the consumer module, replace any local copy of the rule with a call to the owner API, leaving only the adapter.
   - Search the consumer module for the owner's table names and helper names to confirm that no owner-specific queries or traversals remain outside documentation, and search for the owner API names to confirm the calls are in place.
   - Update the owner contract page (where the API lives, which rules it encapsulates, which consumers may use it, and a change-history line), the consumer usage page (that it calls the owner API and does not own the rule), shared knowledge if the workflow is reusable, the `session_state.md` of both modules and the root activity index, and workspace or module instructions if the rule should become a standing instruction.
   - Add cross-links in both directions so the next task starts from the owner API.
   - Before a later change to an existing owner API, check each consumer listed on the owner contract page and update its adapter or usage page in the same task.

## Required Artifacts

- Contract page for the library, class, function, or method.
- Links to permitted source evidence.
- Links to affected table pages or an explicit note that no persistent table side effects are known.
- Inputs, outputs, side effects, errors, dependencies, examples, and confidence labels.
- Open questions for runtime behavior, restricted sources, or unclear callers.
- Index or related-notes updates that make the contract discoverable.
- For a cross-module rule: an owner contract page that lists allowed consumer modules and keeps a change history, a consumer usage page that links to it, and session records in both modules.

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

The same class later becomes an owner API. Suppose the budgeting module is `Alpha` and an approval module `Beta` must show request rows only to users who may see them in `Alpha`'s budget hierarchy. `Alpha` owns the rule, because it owns the hierarchy table, the department mapping, the user's effective budget unit, and the access rules. `Beta` only filters its own request rows.

`Alpha` adds three public methods to its existing access class:

```csharp
public bool RowAccessIsUnrestricted(string userId = null)
public List<int> GetAccessibleUnitsForUser(string userId = null, DateTime? date = null)
public int GetFilterUnitForUser(string userId = null, DateTime? date = null)
```

The first tells a consumer that no filter is needed (for example, for a system administrator). The second returns the units whose rows the user may see: the effective budget unit, its active descendants, and the leaf departments mapped to them. The third returns the default unit for a filter form. How the hierarchy is walked stays inside `Alpha`.

`Beta`'s adapter builds only its own filter:

```csharp
var access = new AlphaAccess();
if (access.RowAccessIsUnrestricted())
    return null;
var units = access.GetAccessibleUnitsForUser();
return Filter("ROW.UNIT in (@UNITS)", units);
```

For a non-administrator, `Beta` also locks the filter-form unit field to the owner-provided value, so saved form values cannot widen access. `Alpha`'s contract page names `Beta` as a consumer; `Beta`'s usage page says it calls `Alpha`'s API and does not own the rule.

## Failure Modes

- Documenting only syntax: the signature is known, but the behavior is still opaque.
- Copying large code bodies: the contract becomes expensive to read and quickly goes stale.
- Omitting side effects: callers miss database writes, status changes, UI calls, or messages.
- Omitting table links: behavior is disconnected from the data contracts it relies on.
- Treating private helpers as stable public APIs.
- Hiding runtime assumptions: behavior appears confirmed even though data, configuration, or permissions were not checked.
- Ignoring access and license limits for platform libraries.
- Updating code without updating a changed public contract.
- Copying another module's rule into a consumer: the queries, hierarchy walks, admin checks, access groups, or level constants now exist twice and drift apart.
- Exposing the owner's internal table structure instead of simple return values, which ties every consumer to the owner's implementation.
- Updating only one side of a cross-module change: the owner contract names no consumers, or the consumer's knowledge base still describes the rule as its own.
- Letting a consumer UI widen what the owner API allows, for example through saved filter values.
- An access adapter that fails open: when the owner API throws or returns an empty list, the consumer drops the filter and shows every row, instead of showing none and reporting the problem.
- Changing an owner API without checking the consumers listed on its contract page.

## Assumptions And Runtime Limits

- A contract page can be partial when uncertainty is explicit.
- Static source evidence can describe code paths, but not every runtime data or configuration case.
- Platform-library behavior can be documented only from permitted evidence.
- A contract page is not a substitute for source review when implementation details matter; it is the entry point that tells the agent whether deeper reading is needed.
- An owner API usually needs runtime wiring: the owner library must load or compile before the consumer, and the consumer must be able to resolve its namespace. Record the working import path in the owner contract page.
- Static search can show that a consumer no longer copies the owner rule, but access-style behavior still needs runtime checks with representative users, such as an administrator, an ordinary user, and a user of a leaf department.

## Related Notes

- `03-knowledge-system.md`: defines module and shared memory, which decides where owner and consumer pages live.
- `04-workspace-bootstrap.md`: defines the module registry (`modules.md`) used to find a rule's owner module.
- `06-knowledge-acquisition.md`: defines permitted evidence and confidence labels.
- `07-tables-as-contracts.md`: explains the data contracts that behavior often relies on.
- `09-usage-flows-and-patterns.md`: downstream section for composing contracts into business scenarios, including consumer usage pages that call an owner API.
- `10-agentic-workflow-with-superpowers.md`: downstream section that defines how a task reaches into an owner module, the lookup order, and the mark left in the owner.
- `12-practical-workspace-template.md`: downstream section for placing contracts in a practical starter workspace.
