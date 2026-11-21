# Security Policy

This repository is documentation: the methodology text, derived
documents, and a copyable workspace template. The template includes a
small integrity tool (`tools/kb/`) that uses the Python standard library,
works only inside the workspace, and makes no network calls.

## In scope

- the integrity tool reading or writing outside the workspace, or running
  code taken from workspace content;
- template instructions (`AGENTS.md`, skills) that lead an agent to send
  data out of the repository or run commands the user did not ask for.

Wording errors and weak advice belong in a normal issue.

## Reporting a vulnerability

Please do not open a public issue for a security problem.

1. Preferred: use **Report a vulnerability** on the repository's
   **Security** tab (GitHub private vulnerability reporting).
2. Or email `tolstolutskyy@gmail.com` with "context-routing security" in
   the subject.

You should get an acknowledgement within 7 days. Confirmed problems are
fixed in the next release and credited in `CHANGELOG.md` unless you ask
otherwise.

The packaged plugin has its own policy in
`ai-erp-collab/deterministic-context-routing-plugin`.
