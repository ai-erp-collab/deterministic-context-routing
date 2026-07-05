# Public Article Outline

## Working Title

How To Make AI Agents Useful In Large Domain-Heavy Software Projects

## Thesis

AI agents become more reliable when the project gives them a durable, file-based knowledge system that routes them to necessary and sufficient context for each task.

## Outline

1. The real blocker is not only code generation.
   - Large systems hide behavior in conventions, schemas, runtime assumptions, business language, and historical decisions.
   - Giving an agent everything is too expensive and often less useful than giving it the right small context.

2. Treat documentation as context routing.
   - Module concepts explain purpose and boundaries.
   - Contract pages describe tables, APIs, and behavior.
   - Usage flows connect objects into business scenarios.
   - Session state keeps work resumable.
   - Git, compilers, tests, and runtime checks strengthen verification when available, but they do not replace task-continuity memory.
   - Confidence labels tell the next agent which claims are confirmed, inferred, runtime-unverified, or blocked-by-access.
   - Documentation is routing infrastructure for future agents, not cleanup after implementation.

3. Keep evidence separate from active context.
   - Raw material can be large.
   - Active task context should be small.
   - Curated pages make repeated work cheaper.

4. Adopt through one real module.
   - Pick one module.
   - Curate one artifact.
   - Run one workflow-backed task.
   - Record verification and assumptions.
   - Expand after the method proves itself.

5. The quality loop.
   - Every task should leave the workspace easier to understand.
   - Verification notes matter when runtime checks are limited.
   - Known issues prevent repeated mistakes.

## Public-Safe Language Rules

- Say "platform libraries", "project libraries", "source examples", "runtime observations", "exported table schemas", "user documentation", and "business requirements".
- Do not expose sensitive origin details.
- Keep examples generic unless a specific example is already approved for public use.

## Possible Ending

The goal is not to build a perfect encyclopedia. The goal is to give the agent enough context to reason safely today, and to leave behind enough durable knowledge that tomorrow's task starts closer to the truth.
