# Working the issue queue

Issues reach you three ways: a hook message after an edit, a blocked
stop at the end of a turn, or the queue in `docs/checks/OPEN.md`.

1. Run `kb fix --safe` first. To see what it would change without
   changing anything, use `kb fix --safe --dry-run`.
2. Run `kb check`. A full check writes a dated report in `docs/checks/`,
   rewrites `docs/checks/OPEN.md`, and gives every open issue a number.
   Use `kb check --changed <files>` to check only what you touched.
3. Read `docs/checks/OPEN.md`: id, severity, module, symptom, proposed
   fix. Work blocking issues first; they mean routing or completeness
   would give an agent wrong context.
4. For an issue with a proposed fix you agree with, apply it with
   `kb fix --ids <N> <N>`; it names each id it could not fix
   (`no automatic fix`) and exits 1. For those and the rest, fix the page
   or evidence yourself, or ask the user when the answer is a judgment
   call (which page is right, what a term means).
5. Run `kb check` again; fixed issues move to the report's resolved list.

Every automatic edit is journaled under `.kb/journal/`; the command
prints `run_id: <id>`. `kb undo <id>` reverts one run if the files have
not changed since.

Links are checked in the knowledge base, in the root and module
`AGENTS.md`, and in the newest part of each `session_state.md` (above its
first stop marker). Outside the knowledge base, a bare file name in
backticks (`concept.md`) is prose, not a link, and a link is changed
automatically only when its own path resolves; session logs are never
fixed automatically. A link that points outside the workspace on purpose
(another repository, a note for a person) is excluded in one of two ways:
a glob in `link_ignore` in `.kb/config.json`, matched against the link as
written (for example `"*other-repo/*"` matches `../../other-repo/a.md`),
or `<!-- kb:ignore-link -->` on the same line. Excluded links are neither
checked nor fixed.

A hook line ending in `(#N)` names an issue already in the queue. A line
without an id is new and gets its number at the next full `kb check`.
