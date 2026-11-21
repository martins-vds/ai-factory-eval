# Fees and payments — acceptance evidence

- Slice: `fees-payments` · Epic: #62 · Acceptance ticket: LF-ACCEPT (#117)
- Report date: 2026-11-21
- Acceptance run: [42912984554, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42912984554)
- Commit: `8f9a11640eef9801378f3db53a76903363c5e5b5`
- Archived result: `.migration/evidence/acceptance-runs/42912984554-1.json`

## Acceptance run

The archived result reports `passed` for the specified commit and attempt. The auditor's acceptance report records that the fetched evidence was independently verified against the run ID, attempt, commit, tracked inputs, and gate evidence. This session did not rerun acceptance gates or mutation.

| Gate | Command | Exit | Notes |
|---|---|---:|---|
| Runtime | `check_runtime.py` | 0 | Python 3.13 |
| Harness integrity | `check_installed.py` | 0 | Installed pins valid |
| Services | `afs-services check` | 0 | Services healthy |
| Graph freshness | `check_graph_fresh.py --require source,target` | 0 | Both graphs fresh |
| Source graph | `graph_gate.py --side source --require-graph` | 0 | 8 entry points; 6 reaching data |
| Target graph | `graph_gate.py --side target --require-graph --enforce-ownership` | 0 | 23 entry points; 18 reaching data; 13 owned, none unowned |
| Build | `python -m compileall -q src`; `python manage.py check` | 0 | Both passed |
| Idiom | `ruff check src config manage.py tests`; `ruff format --check src config manage.py tests` | 0 | Both passed |
| Tests | `pytest -q` | 0 | Full suite passed |
| CRAP | Coverage pytest, `lizard --csv src`, then `crap.py ... --max 30` | 0 | Maximum 7.0; threshold 30 |
| Full mutation | `python .migration/harness/tools/afs-mutation --all` | 0 | Score 0.975; threshold 0.8; 236 killed, 6 survived |

The original acceptance-run journal rows are preserved in `.migration/evidence/runs/LF-AUDIT.md` and copied to this ticket's journal.

## Implementation and verification

LL-03 (#63) landed in PR #88. Its characterization and differential evidence record a two-day grace period, a 25-cent fee per late day capped at $10, the returned-loan date rule, the characterized API responses, and the payment-gateway request and responses.

- **Initial verification, #90 / PR #91:** returned `blocked`. The full suite failed because the live-server loan-catalog browser test could not find a seed loan after test isolation was lost. Changed-code mutation produced no score because mutmut could not collect the selected fee modules.
- **Re-verification, #96 / PR #97:** returned `pass`. The test-isolation fix restored the default-order full suite; build, behavior, idiom, CRAP, changed-code mutation (0.914), and regression checks passed.
- **Audit, #114 / PR #116:** returned `complete`, with no capability gaps or graph inconsistencies. The auditor reviewed the three fees ledger entries, test-first and differential evidence, gateway design, approved quirk rulings, and six full-run mutation survivors. The two fees survivors make internal `Fee` and `GatewayResponse` dataclasses mutable and were judged equivalent for the observable contract; they remain documented.

## Ledger coverage

| Capability | Status | Evidence |
|---|---|---|
| `fees.calculation` | `migrated` | `.migration/ledger/fees.calculation.yaml`; fee characterization and boundary tests |
| `fees.page` | `migrated` | `.migration/ledger/fees.page.yaml`; API, UI, and browser-flow tests |
| `integration.payment-gateway` | `migrated` | `.migration/ledger/integration.payment-gateway.yaml`; gateway request, response, and failure tests |

All three slice entries have target components and differential evidence. The audit found zero coverage gaps.

## Human side-by-side check — requested

Operator: compare the legacy behavior against the target using equivalent loan data, dates, requests, and gateway outcomes; record the observed legacy and target values or responses for each:

1. An overdue loan: late-day count, fee amount, rounding/precision, and displayed dollar amount.
2. A loan that is not overdue: calculated fee and API/page presentation.
3. An unknown loan: exact status and response body, and whether either side calls the gateway.
4. Paying a fee through the API and through the UI: request/interaction and success response or visible page update.
5. A failed gateway payment: non-200 response and I/O/interruption failure behavior, including status/body or UI state.

The human check is requested and has not been marked passed. This report does not approve or sign off the slice.
