# Workspace Bootstrap


## Reader Outcome

After this section, the reader can:

- Create the minimum workspace files that make the memory model operational.
- Explain the purpose of each bootstrap file before creating or using it.
- Register modules with paths, aliases, wiki roots, source roots, and artifact roots.
- Add markers, indexes, aliases, and conditional reading instructions that prevent over-reading.
- Create agent instruction files last, after the files they reference are defined.

## Core Explanation

The knowledge system defines memory layers. The workspace bootstrap turns those layers into concrete files and folders.

The bootstrap should not begin with a rule file that references unexplained files. First define the artifacts the rule file will coordinate. Then create the agent instruction file that tells the agent how to use them. This keeps the setup readable and follows the local rule: define each entity before using it in instructions.

The core bootstrap entities are:

- `known_issues.md`: a short operational list of recurring workspace risks and required handling.
- `modules.md`: the module registry; it maps module names and aliases to paths, wiki roots, source roots, shared wiki roots, and artifact roots.
- `session_state.md`: short memory; it stores compact restart context and stops at `<!-- AGENT-SESSION-STOP -->`.
- Project capability profile: a short record of available verification and history tools, such as Git, compiler, automated tests, runtime access, database snapshots, encoding checks, and artifact exporters.
- Module wiki root: module memory for local concepts, contracts, usage flows, decisions, and open questions.
- Shared wiki root: shared product memory for reusable platform or cross-module knowledge.
- Source artifact folders: source evidence areas for raw exports and processed exports.
- Design and plan folders: medium memory for task reasoning.
- Agent instruction file: local rules for an agent. In this workspace the file is `AGENTS.md`; in another agent environment it may be `CLAUDE.md`, `GEMINI.md`, workspace instructions, or another supported rule file.

After these entities exist, the agent instruction file can safely reference them. It becomes the orientation contract: read known issues, resolve the module, load only latest session state, use the right memory roots, preserve encoding, and record verification limits.

The safest default is the hard case: assume there may be no Git history, no compiler, no local runtime, and no complete automated test suite until the project proves otherwise. That default keeps the method usable in restricted proprietary environments. It is not a reason to ignore better tools when they exist. If Git is available, use it for file-change history and diffs. If a compiler, build command, test runner, or target runtime is available, make those checks part of the verification rules. The capability profile records which of these tools are available and where the agent should use them.

`session_state.md` remains required even in a Git-enabled project. Git history answers version-control questions: which files changed, who committed, when a commit happened, and what diff was recorded. Short memory answers task-continuity questions that commits often do not answer: why the work was started, which evidence was used, which assumptions remain unverified, what was discussed without a code change, which checks were skipped, and what the next useful action is. Not every investigation becomes a commit, not every useful discovery changes files, and commit messages are not designed as agent restart context.

The bootstrap also implements the context-routing pattern from the knowledge system section. Files are not enough. The workspace must include stop markers for growing history files, indexes for wiki roots, aliases for natural-language module names, artifact ledgers for source evidence, and instructions that say when to read optional or expensive context. These controls keep "available context" from becoming "mandatory context."

## Reproducible Procedure

1. Create `known_issues.md`.
   - Purpose: recurring risks that every future agent must handle.
   - Keep it short and operational.
   - Record only recurring workspace problems that future agents must handle.
   - For each issue, name the symptom, cause, and required handling.
   - Link detailed rationale to shared wiki pages when needed.

2. Create `modules.md`.
   - Purpose: routing table from natural-language module names to workspace paths.
   - Register every module by canonical name.
   - For each module, record module path, wiki root, shared wiki root, source roots, artifact roots, and aliases.
   - Use aliases that users naturally type, including product names, short names, and domain labels.

3. Create root `session_state.md`.
   - Purpose: compact workspace restart context.
   - Put the current entry first.
   - Include `Last active module`.
   - End each entry with the exact marker `<!-- AGENT-SESSION-STOP -->`.
   - In future reads, stop at the first marker so old context cannot override current state.

4. Create a project capability profile.
   - Purpose: make available tools explicit instead of assuming the hardest environment forever.
   - Start with the hard-case baseline: no Git, no compiler, no local runtime, no reliable automated tests.
   - If Git exists, define when to use `git status`, `git diff`, and recent log review.
   - If a compiler, build command, test runner, or runtime exists, define the exact verification commands and what their passing or failing output means.
   - If a tool exists only for some modules, record that at module level instead of making it a workspace-wide rule.
   - Keep `session_state.md` mandatory because it records task intent, evidence, assumptions, verification, and next action, not just file changes.

5. Create module roots.
   - Purpose: bounded work areas with their own memory and rules.
   - Create each module folder.
   - Create each module's `session_state.md` for short module memory.
   - Keep the module state entry focused on current status, source material used, decisions, open questions, verification, and next action.

6. Create wiki roots.
   - Purpose: long memory.
   - Use `knowledge-base/shared` for reusable platform or cross-module knowledge.
   - Use `knowledge-base/modules/<module>` for module-specific knowledge unless the module has an explicit local wiki root.
   - Add `INDEX.md` files so agents can enter the wiki cheaply.
   - Add related-notes links from summary pages to deeper evidence pages.

7. Create source artifact folders.
   - Purpose: source evidence.
   - Put newly found XML, CSV, TXT, or similar exports in `source-artifacts/tables/raw`.
   - Move recognized exports to `source-artifacts/tables/processed` only after wiki pages are created or refreshed.
   - Maintain `source-artifacts/INDEX.md` as the artifact ledger.

8. Create design and plan folders.
   - Purpose: medium memory for task-specific reasoning.
   - Use root `docs/` for workspace-wide designs and plans.
   - Use module `docs/` when the document belongs to one module.

9. Create root agent instruction file.
   - Purpose: tell the agent how to orient in the workspace.
   - In this workspace, use root `AGENTS.md`.
   - In other environments, use the rule-file mechanism supported by that agent, such as `CLAUDE.md`, `GEMINI.md`, workspace instructions, or an equivalent.
   - Define the orientation order: read known issues, resolve the active module, read module rules, load latest session state, and use the correct memory roots.
   - Define conditional reading rules for source roots, wiki roots, historical notes, and optional supporting documents.
   - Define verification expectations for the project's capability profile, including what to do when Git, a compiler, tests, or the proprietary runtime are unavailable.
   - Add encoding handling for Cyrillic-sensitive files.

10. Create each module's agent instruction file.
   - Purpose: module-local operating rules.
   - In this workspace, use `<module>/AGENTS.md`.
   - Name the module explicitly.
   - Define module-specific product folders, wiki folders, artifact folders, and docs folders.
   - State whether the module is code-producing, documentation-only, or artifact-curation-only.
   - Require module `session_state.md` updates after non-conversational work.

11. Add static verification guardrails.
   - Purpose: compensate for limited tool or runtime access.
   - Preserve UTF-8 for active Markdown and source files unless an artifact workflow requires another encoding.
   - Add or document an encoding scan for Cyrillic-sensitive changes.
   - If Git, compiler checks, automated tests, or full runtime tests are impossible, require static checks and explicit assumptions.

## Required Artifacts

- Root `known_issues.md`.
- Root `modules.md`.
- Root `session_state.md`.
- Project capability profile or project-specific tool availability rules.
- Module `<module>/session_state.md`.
- Shared wiki root, usually `knowledge-base/shared`.
- Module wiki root, usually `knowledge-base/modules/<module>` or a module-specific wiki path.
- Raw and processed artifact folders, usually `source-artifacts/tables/raw` and `source-artifacts/tables/processed`.
- Artifact index, usually `source-artifacts/INDEX.md`.
- Design and plan folders.
- Wiki `INDEX.md` pages and related-notes links.
- Session-state stop marker, exactly `<!-- AGENT-SESSION-STOP -->`.
- Conditional reading rules for optional or expensive context.
- Root agent instruction file, for example `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or equivalent.
- Module agent instruction file, for example `<module>/AGENTS.md` or equivalent.
- Encoding/static verification workflow, for example `tools/check_encoding.ps1`.
- Build, compiler, test, runtime, or Git verification commands when the target project has them.

## Example

An example proprietary ERP workspace uses this bootstrap shape:

```text
Workspace/
  known_issues.md
  modules.md
  session_state.md
  AGENTS.md
  knowledge-base/
    shared/
    modules/
      Alpha/
      Beta/
  source-artifacts/
    tables/
      raw/
      processed/
  Methodology/
    AGENTS.md
    session_state.md
    Wiki/
    Methodology/sections/
```

`modules.md` registers `Alpha`, `Beta`, and `Methodology`. If a user says "continue the methodology work" and no module path is supplied, root `session_state.md` resolves the last active module to `Methodology`. The module `AGENTS.md` then says this is a documentation-only module, that source sections live in `Methodology/Methodology/sections/`, and that work must proceed one section at a time.

This is a small example, but it captures the important behavior: the agent does not infer the module from open editor tabs alone, does not read the entire historical session log, and does not put module-specific facts into shared knowledge by accident.

It also captures the anti-overread behavior. `modules.md` routes natural-language aliases to one module. `session_state.md` stops at the current entry. `INDEX.md` pages route the agent into curated wiki pages. Artifact indexes route from a table name to recognized evidence. Agent instructions say when to read deeper sources and when to stay with curated memory.

The agent instruction file appears after `known_issues.md`, `modules.md`, `session_state.md`, wiki roots, and artifact roots are defined. That order is intentional: the rule file coordinates known entities instead of introducing them by surprise.

In a project with Git and a compiler, the same bootstrap would add a project-specific capability profile. The root rules would say which Git commands may be used to inspect local changes, which build or compiler command validates syntax, which tests are reliable, and which runtime checks still require a human or target environment. The session-state rule would stay in place because the agent still needs restart context for investigations, design discussions, assumptions, and next actions that may never appear in a commit.

## Failure Modes

- Creating agent instructions first: the file references entities the reader has not yet understood.
- No known-issues file: recurring risks are rediscovered after damage has already happened.
- No module registry: natural-language requests cannot be routed reliably to paths, sources, wiki roots, or artifact roots.
- No aliases: users type domain names that are obvious to the team but invisible to the agent.
- No stop marker in session state: old decisions and stale open questions are loaded as if they were current.
- Session state becomes a diary: short memory becomes expensive and noisy.
- Git log is treated as session memory: version-control history is asked to explain task intent, open assumptions, or uncommitted investigations that it does not reliably contain.
- Available tools are not recorded: the agent keeps using hard-case static checks even though a compiler, test runner, Git history, or runtime check exists.
- No indexes or related links: wiki folders become broad reading assignments.
- No conditional reading rules: source roots and historical notes become default context instead of optional evidence.
- Shared and module knowledge are mixed: reusable platform facts become trapped in one module, or module-specific rules are overgeneralized.
- Raw artifacts are edited in place: source evidence becomes hard to audit after recognition.
- Encoding guardrails are missing: Cyrillic text can become mojibake during otherwise unrelated documentation or source edits.
- Runtime limits are hidden: static checks are mistaken for full runtime verification.

## Assumptions And Runtime Limits

- This method assumes a file-based workspace where agents can read and update Markdown rules, wiki notes, and source artifacts.
- Git is useful but not required. In the hard-case workspace, git is not expected, so verification relies on filesystem checks, static scans, and session-state notes.
- Compiler, build, test, and runtime access are useful but not guaranteed. When they exist, the project instructions should name the exact commands and require the agent to use them where relevant.
- Proprietary runtime behavior may remain unverified. When that happens, the limitation must be named in the section, plan, wiki page, or session state that depends on it.
- The bootstrap does not document business behavior by itself. It only creates the durable places where business behavior can be documented.

## Related Notes

- `01-why-this-method-exists.md`: explains why context management is necessary.
- `03-knowledge-system.md`: defines the memory layers this bootstrap implements.
- `05-module-concept-and-language.md`: downstream section for module language as the natural-language interface.
- `Methodology/Wiki/research.md`: workspace evidence used by this section.
- `Methodology/Wiki/review-notes.md`: first-draft gap that required a bootstrap walkthrough.
