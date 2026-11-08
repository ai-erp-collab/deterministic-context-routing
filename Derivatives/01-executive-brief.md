# Agentic Proprietary ERP Methodology: Executive Brief

## Audience

This brief is for decision makers, technical leads, and project sponsors deciding whether to adopt the methodology.

## Core Claim

The methodology makes agent-assisted work practical in large, under-documented, domain-heavy systems by providing deterministic context routing instead of relying on chat history, broad search, or raw source dumps.

## Why It Matters

Proprietary ERP work is often limited less by code generation and more by missing context: business vocabulary, table contracts, platform conventions, project libraries, runtime assumptions, and historical decisions. The methodology turns those facts into durable, file-based routing infrastructure that future agents can reuse.

That infrastructure degrades if nothing guards it. Agents behave differently from session to session: links that tools cannot open, pages missing from indexes, the same table described twice, evidence nobody registered. Rules in prose do not stop this, agent self-checks drift with the agent, and manual review costs developer time. The methodology therefore moves mechanical upkeep into a small deterministic tool that runs on agent events, fixes what has exactly one correct answer (journaled and reversible), and hands only judgment calls to the agent and the user.

## What It Produces

- a module registry;
- module concepts written in business language;
- table and class contract pages;
- usage-flow notes;
- an evidence registry with a hash per artifact and checked completeness;
- a deterministic integrity layer: checks on agent events, safe journaled fixes, a numbered issue queue, and upgrades with snapshot and rollback;
- implementation plans;
- verification records;
- confidence labels: `confirmed`, `inferred`, `runtime-unverified`, and `blocked-by-access`;
- compact session state.

## Practical Benefits

- lowers repeated discovery cost;
- reduces dependence on chat history;
- keeps agent context bounded;
- makes uncertainty explicit with confidence labels;
- produces documentation as a working product of real work;
- treats documentation as routing infrastructure for future agents, not cleanup;
- supports adoption one module at a time;
- keeps the knowledge base from degrading without agent attention or developer time;
- works in the hard case with no Git and no compiler/runtime, while allowing stronger verification when a project has Git, compiler/build commands, tests, or runtime access;
- keeps session state separate from Git history: commits record file changes, while session state records intent, evidence, assumptions, verification, and next action.

## Adoption Path

1. Pick one active module.
2. Write or refresh its module concept.
3. Record the project's capability profile: Git, compiler/build, tests, runtime access, static checks, encoding rules, and source artifact paths.
4. Install the integrity layer (the free plugin is the fastest path) and register one real artifact.
5. Curate that artifact into a small wiki page.
6. Label important claims as `confirmed`, `inferred`, `runtime-unverified`, or `blocked-by-access`.
7. Run one workflow-backed task using that curated context.
8. Use every available verification capability and record what remains unverified.
9. Record session state even when Git history exists.
10. Audit what became easier, safer, or still uncertain.

## Risks

- Treating the method as documentation theater.
- Writing documentation that explains but does not route future work.
- Treating inferred or runtime-unverified claims as confirmed.
- Trying to document the entire system before proving value on one module.
- Copying source dumps instead of curating small knowledge pages.
- Forgetting to record runtime assumptions.
- Letting derivatives drift away from the master methodology.
- Keeping the knowledge base healthy by rules in prose alone: it degrades silently under task pressure.

## Decision

Adopt the methodology first on one module with one real task. Expand only after the workflow proves that it reduces rediscovery and improves verification quality.
