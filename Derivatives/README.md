# Methodology Derivatives

Derived documents are reader-specific outputs generated from the master methodology.

The source of truth remains:

- `Methodology/sections/`
- `Assembly/manifest.md`
- `Output/agentic-proprietary-erp-master-methodology.md`

## Documents

| Document | Audience | Status | Source Sections | Refresh Rule |
| --- | --- | --- | --- | --- |
| `01-executive-brief.md` | decision makers, leads, sponsors | draft | `00`, `01`, `02`, `10`, `12` | refresh after changes to positioning, benefits, adoption, or template audit |
| `02-practical-adoption-checklist.md` | implementers adopting the method on one module | draft | `03`, `04`, `05`, `10`, `11`, `12` | refresh after changes to workspace structure, artifact workflow, or adoption steps |
| `03-public-article-outline.md` | public article, talk, or presentation preparation | draft | `00`, `01`, `02`, `09`, `10`, `12` | refresh after changes to public positioning or workflow narrative |

## Rules

- Do not treat derivatives as new source truth.
- Include the project capability profile idea: the hard-case baseline is no Git and no compiler/runtime, but available Git, compiler/build, tests, and runtime checks should be enabled explicitly.
- Keep `session_state.md` mandatory because it records task continuity, not version-control history.
- Use deterministic context routing as the positioning phrase: `modules.md` -> module concept -> wiki/contracts -> artifact index -> session state.
- Treat documentation as routing infrastructure for future agents, not cleanup prose.
- Include confidence labels for important claims: `confirmed`, `inferred`, `runtime-unverified`, and `blocked-by-access`.
- Keep origin-detail wording neutral.
- Prefer short, reusable documents over copying the full methodology.
- If a derivative reveals a source problem, fix the source section first and rebuild the master output.
- Record each derivative's source sections in `source-map.md`.
