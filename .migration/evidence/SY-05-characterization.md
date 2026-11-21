# SY-05 Tier A characterization

The pinned legacy application was built and started by
`.migration/characterization/source/characterize.py`. The harness exercised seven graph endpoints
and two browser pages, plus five error or missing/unknown-input cases.

## Legacy test inventory

No legacy test sources or test resources were found under `legacy/`; `legacy/pom.xml` does not add
JUnit or another test framework. No `legacy-test:` evidence can be cited.

## Observed behavior

- `GET /loans` returned 200 with the three seed loans ordered by ID and semicolon-separated fields.
- `GET /loans/{id}` returned the matching loan as text 200; an unknown ID returned text 404.
- `POST /loans` with member and ISBN returned 201 and a new `L4` loan dated today; missing ISBN returned 400.
- `POST /loans/{id}/return` marked `L1` returned today and returned 200; an unknown ID returned 404.
- `GET /fees/{id}` returned 200 HTML for `L3`; an unknown ID returned 404 HTML.
- `POST /payments/{id}` for `L3` returned 502 `payment gateway unavailable`; an unknown ID returned 404.
- `GET /about` returned 200 HTML with the Lending Library heading and static contact/lending details.

## Predicted versus observed

- Normal and edge HTTP cases matched the ledger and source-reading predictions: 12.
- Browser observations matched source and ledger predictions: 2.
- Differences: 0.
- Best tier: A for every runtime-observable capability. The monthly report remains spec-derived at tier C
  because it is specified only in `legacy/docs/reports-spec.md`.

Run evidence: `.migration/evidence/runs/SY-05.md`.
