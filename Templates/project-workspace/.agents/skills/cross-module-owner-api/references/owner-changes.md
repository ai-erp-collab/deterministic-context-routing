# Owner Changes (command mode)

Read from `../SKILL.md` section 4. These are its three steps.

## 4.1 Change the owner

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

## 4.2 Mark the owner (every write into the owner, code or knowledge)

1. Owner contract page: add the consumer to `consumers:` and one line to
   `## Change History` (date, consumer, what changed, why).
2. Owner `session_state.md`: append an entry from
   `templates/session/cross-module-entry.md`. Copy the owner's previous
   `Next useful action` word for word into it, so the owner keeps its
   own restart point.
3. Consumer `session_state.md`: the normal task entry, naming the owner
   module and the owner API.
4. Root `session_state.md`: name both modules.

## 4.3 Checks

- Search the consumer for the owner's table and helper names: nothing
  owner-specific may remain outside documentation.
- Search the consumer for the owner API names: the calls are in place.
- Record runtime wiring (load order, namespace or import path) on the
  owner contract page.
- Mark access behavior `runtime-unverified` until checked with an
  unrestricted user, an ordinary user, and a user at the bottom of the
  hierarchy.
