# Slice fees-payments — acceptance evidence

- Tickets: LL-03 (#63), initial verification (#90), re-verification (#96), audit (#114), acceptance (LF-ACCEPT, #117)
- Acceptance run: [42912984554, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42912984554)
- Commit: `8f9a11640eef9801378f3db53a76903363c5e5b5`
- Archived result: `.migration/evidence/acceptance-runs/42912984554-1.json`
- Evidence date: 2026-11-21

## Acceptance run

The archived result records a successful acceptance run for the exact commit above. The archive was independently verified by the LF-AUDIT work; the current session did not rerun gates or mutation.

| Gate | Command | Exit | Result |
|---|---|---:|---|
| Runtime | `check_runtime.py` | 0 | Python 3.13 |
| Harness integrity | `check_installed.py` | 0 | Installed pins valid |
| Services | `afs-services check` | 0 | Healthy |
| Graph freshness | `check_graph_fresh.py --require source,target` | 0 | Both graphs fresh |
| Source graph | `graph_gate.py --side source --require-graph` | 0 | 8 entry points; 6 reaching data |
| Target graph | `graph_gate.py --side target --require-graph --enforce-ownership` | 0 | 23 entry points; 18 reaching data; 13 owned, none unowned |
| Build | `python -m compileall -q src`; `python manage.py check` | 0 | Both passed |
| Idiom | `ruff check src config manage.py tests`; `ruff format --check src config manage.py tests` | 0 | Both passed |
| Tests | `pytest -q` | 0 | Full suite passed |
| CRAP | Coverage pytest, `lizard --csv src`, then `crap.py ... --max 30` | 0 | Maximum 7.0; threshold 30 |
| Full mutation | `python .migration/harness/tools/afs-mutation --all` | 0 | 0.975; threshold 0.8; 236 killed, 6 survived |

The archived JSON is the source for these run results. The corresponding gate rows and log hashes are in `.migration/evidence/runs/LF-AUDIT.md`.

## Implementation, verifications, and audit

- LL-03 (#63) landed in PR #88. Its migrator return records build, behavior, idiom, CRAP, changed-code mutation, and regression results.
- The initial verification (#90, PR #91) was blocked by the test-isolation issue involving seed loans in the live-server test.
- Re-verification (#96, PR #97) returned `pass` after the test-isolation fix; the full suite passed and changed-code mutation scored 0.914.
- The independent audit (#114, PR #116) returned `complete`, with no capability gaps or graph inconsistencies. See `.migration/evidence/fees-payments/report.md` and `.migration/returns/LF-AUDIT.afs-auditor.yaml`.

## Capability coverage

All three fees ledger entries are `migrated`, have target components, and include differential evidence:

| Capability | Status | Target evidence |
|---|---|---|
| `fees.calculation` | `migrated` | `FeeApplication.fee_for`; fee calculation boundary and returned-date tests |
| `fees.page` | `migrated` | API and browser fee pages; characterized response and UI payment-flow tests |
| `integration.payment-gateway` | `migrated` | Application-owned gateway port, HTTP adapter, and request/response/failure tests |

The auditor checked each entry against the target graph and cited evidence. There are no coverage gaps.

## Full mutation and survivors

The archived full mutation score is 0.975 (threshold 0.8): 236 mutants killed and 6 survived. The audit identified four survivors outside this slice and two fees survivors that make internal `Fee` and `GatewayResponse` dataclasses mutable. The audit assessed the latter as equivalent for the observable contract; they remain documented survivors, not silently counted as killed. The audit details are in `.migration/evidence/fees-payments/report.md`.

## Human side-by-side check — requested

Compare legacy against target using equivalent loan data, dates, requests, and gateway outcomes. Record the observed value or response on each side:

1. For an overdue loan, compare late-day count, amount in cents, displayed amount, and rounding/precision.
2. For a loan that is not overdue, compare the calculated fee and its API/page presentation.
3. For an unknown loan, compare status and exact response body, and whether either side contacts the gateway.
4. Pay a fee through the API and through the UI; compare the request/interaction and the success response or visible page update.
5. Cause the payment gateway to fail with a non-200 response and with an I/O/interruption failure; compare the API status/body and the UI result.

No human comparison has been reported. This request does not approve the slice or mark the human check complete.
