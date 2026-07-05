# Contributing

Thank you for your interest in the Deterministic Context Routing
methodology. This project accepts issues and pull requests under the terms
of `LICENSE` and `ADDITIONAL-USE-GRANT.md`.

## Before You Start

- Read `Methodology/sections/00-preface.md` for the reading path and scope.
- Read `Templates/section-contract.md` and `Templates/section-dod.md` if
  you are proposing a change to a methodology section — every section must
  satisfy both.
- Check open issues before starting substantial work, to avoid duplicate
  effort.

## What We Accept

- Corrections to existing sections, derivatives, or templates: wording,
  factual errors, broken cross-references, inconsistent terminology.
- New examples that follow the neutral-wording rule: no real proprietary
  platform, company, or internal system names in examples.
- New derivative documents, proposed as a pull request that also updates
  `Derivatives/README.md`, `Derivatives/derivatives-manifest.md`, and
  `Derivatives/source-map.md`.
- Improvements to `Templates/project-workspace/` that keep it copyable and
  self-contained.

## What We Don't Accept

- Changes that remove or weaken the confidence-label taxonomy
  (`confirmed`, `inferred`, `runtime-unverified`, `blocked-by-access`)
  without an equivalent replacement.
- Section rewrites that skip the `Reader Outcome` / `Quality Checklist`
  structure defined in `Templates/section-contract.md`.
- Examples naming a real internal project, module, or platform identifier.

## Licensing Of Contributions

By submitting a pull request, you agree that your contribution is
licensed under the same terms as this repository (`LICENSE` and
`ADDITIONAL-USE-GRANT.md`), and you grant the Licensor the right to
relicense your contribution as part of the Licensed Work — including
under the Change License once the Change Date is reached. If you're not
able to agree to this, please open an issue describing the change instead
of a pull request.

## Pull Request Process

1. Fork the repository and create a branch named for the change
   (`fix/...`, `docs/...`, `feature/...`).
2. Make the smallest change that addresses the issue.
3. If you changed a `Methodology/sections/*.md` file, confirm it still
   satisfies `Templates/section-contract.md` and `Templates/section-dod.md`.
4. Open a pull request describing what changed and why.
5. A maintainer will review against the criteria above and may ask for
   changes before merging.

## Reporting Issues

Open a GitHub issue describing the section or document affected, what is
wrong or missing, and (if you have one) a suggested fix.

## Code Of Conduct

Participation in this project is governed by `CODE_OF_CONDUCT.md`.
