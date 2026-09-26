---
name: cross-module-owner-api
description: Use when a task in the active module needs a rule that belongs to another module (for example user access to documents, a hierarchy walk, route statuses), when the user asks whether such a rule already exists somewhere, or when the user tells you to reuse or extend another module. Finds the owner module deterministically, keeps the rule in the owner behind an owner API, and, once the rule is taken into work, leaves a link in the consumer and a mark in the owner.
---

# Cross-Module Owner API

The **consumer module** is the active module where the task started.
The **owner module** is the module whose domain the rule belongs to.
The **owner API** is a small public method set in the owner module that
the consumer calls instead of copying the rule.

## 1. Mode: question or command

- **Question** ("do we already have access rules for documents
  somewhere?"): look, report, and propose. Do not change code in the
  owner module.
- **Command** ("look at module X and add a helper there", "reuse what X
  has"): you may change the owner module within the scope of the
  command.
- Never enter another module on your own initiative. If the task seems
  to need one and the user said neither, ask.

## 2. Lookup order (stop at the first hit)

1. Consumer links: the consumer's knowledge-base pages and module
   `AGENTS.md` may already link to an owner contract page.
2. Named module: if the user named the module, go to its
   `knowledge-base/modules/<owner>/INDEX.md`.
3. Registry: otherwise resolve the candidate owner in `modules.md`, then
   read its `INDEX.md`.
4. Owner contract, usage, and table pages linked from that `INDEX.md`.
5. Owner source code, only if the knowledge base lacks the fact.

Report which step produced the answer.

## 3. Record the link in the consumer

Do this only when the owner rule is taken into work: a command, or the
user decides to reuse the rule. A plain question leaves no trace in the
consumer; the user may have asked for reasons that have nothing to do
with this module.

Add a link to the owner contract page in the consumer's usage or concept
page. If every future task in the consumer should know it, also add one
line under `## Cross-Module Links` in the consumer module `AGENTS.md`.

## 4. Change the owner (command mode only)

1. Read the owner module `AGENTS.md`; its rules govern its files.
2. Find the existing helper where the rule already lives. If the rule
   exists only as a copy in the consumer, move it into the owner first.
3. Add a public method named after the consumer scenario. Build it on
   the existing private helpers. Return simple values (flag, id, list of
   ids, small data object), not internal table structure.
4. In the consumer, keep only an adapter: call the owner API, pass local
   parameters, apply the result to the local filter, form, or step. For
   access rules, fail closed: on error or empty result show nothing and
   report, never drop the filter.
5. If you change an existing owner API, check every consumer listed on
   its contract page and update their adapters in the same task.

## 5. Mark the owner (every write into the owner, code or knowledge)

1. Owner contract page: add the consumer to `consumers:` and one line to
   `## Change History` (date, consumer, what changed, why).
2. Owner `session_state.md`: append an entry from
   `templates/session/cross-module-entry.md`. Copy the owner's previous
   `Next useful action` word for word into it, so the owner keeps its
   own restart point.
3. Consumer `session_state.md`: the normal task entry, naming the owner
   module and the owner API.
4. Root `session_state.md`: name both modules.

## 6. Checks

- Search the consumer for the owner's table and helper names: nothing
  owner-specific may remain outside documentation.
- Search the consumer for the owner API names: the calls are in place.
- Record runtime wiring (load order, namespace or import path) on the
  owner contract page.
- Mark access behavior `runtime-unverified` until checked with an
  unrestricted user, an ordinary user, and a user at the bottom of the
  hierarchy.
