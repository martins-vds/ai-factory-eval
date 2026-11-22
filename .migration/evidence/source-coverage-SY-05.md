# Source coverage (best effort)

- No legacy test sources were found under `legacy/src/test` or elsewhere in the source tree.
- JaCoCo 0.8.13 instrumented the expanded tier-A characterization runner, including seven graph endpoints, two browser pages, 16 edge cases, two restart cases, and four payment-gateway cases.
- JaCoCo reported 94 covered / 4 missed lines, 497 covered / 16 missed instructions, 18 covered / 2 missed branches, 35 covered / 2 missed methods, and 7 covered / 0 missed classes.
- The refreshed source risk map reports maximum CRAP 4.0, with 0 methods over 30: `.migration/risk-map/SY-05.md`.
- Evidence: `.migration/evidence/runs/SY-05.md` rows `source-coverage-characterization`, `source-jacoco-report`, `source-coverage-summary`, and `source-crap-risk-map`.
