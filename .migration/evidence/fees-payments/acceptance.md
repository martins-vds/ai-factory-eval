# Fees and payments — acceptance evidence

- Slice: `fees-payments` · Epic: #62 · Acceptance ticket: LF-ACCEPT (#117)
- Acceptance run: [42912984554, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42912984554)
- Commit: `8f9a11640eef9801378f3db53a76903363c5e5b5`
- Archived result: `.migration/evidence/acceptance-runs/42912984554-1.json`

## Acceptance run

The archived run result is `passed` for the exact commit above. The original run and gate evidence are recorded in the archive and `.migration/evidence/runs/LF-AUDIT.md`; the Auditor independently verified the archive. This session did not rerun gates or mutation.

| Gate | Command | Exit | Notes |
|---|---|---:|---|
| Runtime | `check_runtime.py` | 0 | Python 3.13 |
| Harness integrity | `check_installed.py` | 0 | Installed pins valid |
| Services | `afs-services check` | 0 | Test services healthy |
| Graph freshness | `check_graph_fresh.py --require source,target` | 0 | Both sides fresh |
| Source graph | `graph_gate.py --side source --require-graph` | 0 | 8 entry points; 6 reach data |
| Target graph | `graph_gate.py --side target --require-graph --enforce-ownership` | 0 | 23 entry points; 18 reach data; 13 owned, none unowned |
| Build | `python -m compileall -q src`; `python manage.py check` | 0 | Both steps passed |
| Idiom | `ruff check src config manage.py tests`; `ruff format --check src config manage.py tests` | 0 | Both steps passed |
| Tests | `pytest -q` | 0 | Full suite |
| CRAP | Coverage pytest, `lizard --csv src`, then `crap.py ... --max 30` | 0 | Maximum 7.0; threshold 30 |
| Full mutation | `python .migration/harness/tools/afs-mutation --all` | 0 | Score 0.975; threshold 0.8; 236 killed, 6 survived, 15 files |

## Characterization (tier A)

The LL-03 differential record and source goldens document the characterized behavior:

- Fee calculation uses the source-predicted date rule, a two-day waiver, 25 cents per late day, and a $10 cap. Target unit tests cover 0, 1, 2, 3, 11, and 100 late days, and use `returned_on` for returned loans.
- `GET /fees/{id}` matches the characterized HTML; an unknown loan returns the characterized 404 body. The browser fee page displays the same capped amount.
- Payment sends an empty-body `POST /charge?loan={id}` to the configured or default gateway URL. A gateway 200 maps to 200; other responses map to 502; an unknown loan returns 404 without a gateway call.
- The approved interruption ruling (#40) changes the source's swallowed-interruption behavior: the target returns 502 and preserves `InterruptedError` as the gateway failure cause.

Evidence: `.migration/evidence/runs/LL-03.md`, `.migration/characterization/source/goldens/http.json`, `.migration/characterization/source/goldens/edge-cases.json`, `.migration/characterization/source/goldens/gateway.json`, and the differential tests cited by the ledger.

## Verifications and audit

- LL-03's initial verification (#90, PR #91) was blocked by the test-isolation regression.
- Re-verification (#96, PR #97) passed after the test-isolation fix; the default-order full suite passed.
- The independent audit (#114, PR #116) returned `complete`, with no gaps or graph inconsistencies across the three fees capabilities.
- The full mutation run left six survivors. Four are outside this slice. The two fees survivors make internal `Fee` and `GatewayResponse` dataclasses mutable; the Auditor assessed them as equivalent for the observable contract because neither value is mutated.

## Capability coverage (gate 7)

All three fees ledger entries are `migrated`, have target components, and cite differential evidence:

| Capability | Target components | Evidence | Status |
|---|---|---|---|
| `fees.calculation` | `FeeApplication.fee_for`, fee API and page views | Fee calculation tests, characterization goldens, LL-03 journal | `migrated` |
| `fees.page` | Fee detail/page views, routes, detail template | API response, browser flow, and seed-restoration tests; characterization goldens | `migrated` |
| `integration.payment-gateway` | `FeeApplication.pay`, gateway protocol/adapter, repository and composition, payment views | Gateway request/response, unknown-loan, and interruption tests; gateway golden | `migrated` |

The Auditor checked all three entries against the acceptance graph and their evidence. The graph reaches the loan data for all four slice anchors; the gateway request/response path is evidenced by adapter code, the golden, and tests.

## Human check — requested

The operator should compare **legacy against target side by side**, using the same loan data, as-of date, and gateway outcome, and record the actual values and responses observed in each:

1. For an overdue loan, compare late-day count, fee amount in cents, displayed dollar amount, and rounding/precision.
2. For a loan that is not overdue, compare the calculated fee and its API/page presentation.
3. For an unknown loan, compare status and exact response body for fee lookup and payment; confirm whether either side contacts the gateway.
4. Pay a fee through the API and through the UI; compare the request/interaction and success response or visible page update.
5. Make the gateway fail with a non-200 response and an I/O/interruption failure; compare status, body, or UI state. Record the approved interruption divergence under #40 rather than treating it as an unruled difference.

No human side-by-side result has been reported. `human_check` remains `requested`; this report does not record approval or sign-off.
