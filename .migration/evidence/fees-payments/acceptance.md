# Slice fees-payments — acceptance evidence

- Tickets: LL-03 (#63), verification (#90, #96), LF-AUDIT (#114), LF-ACCEPT (#117) · Commit: `8f9a11640eef9801378f3db53a76903363c5e5b5` · Date: 2026-11-21
- Acceptance run: [42912984554, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42912984554)
- Archived result: `.migration/evidence/acceptance-runs/42912984554-1.json`

## Gates

The archived run passed for the exact commit above. These results are recorded in `.migration/evidence/runs/LF-AUDIT.md`; this coordinator did not rerun gates or mutation.

| Gate | Command | Exit | Notes |
|---|---|---:|---|
| Runtime | `check_runtime.py` | 0 | Python 3.13 |
| Harness integrity | `check_installed.py` | 0 | Installed pins valid |
| Services | `afs-services check` | 0 | Test services healthy |
| Graph freshness | `check_graph_fresh.py --require source,target` | 0 | Both sides fresh |
| Source graph | `graph_gate.py --side source --require-graph` | 0 | 8 entry points; 6 reaching data |
| Target graph | `graph_gate.py --side target --require-graph --enforce-ownership` | 0 | 23 entry points; 18 reach data; 13 owned, none unowned |
| Build | `python -m compileall -q src`; `python manage.py check` | 0 | Both passed |
| Idiom | `ruff check src config manage.py tests`; `ruff format --check src config manage.py tests` | 0 | Both passed |
| Tests | `pytest -q` | 0 | Full suite passed |
| CRAP | Coverage pytest, `lizard --csv src`, then `crap.py ... --max 30` | 0 | Maximum 7.0; threshold 30 |
| Full mutation | `python .migration/harness/tools/afs-mutation --all` | 0 | 0.975; threshold 0.8; 236 killed, 6 survived |

## Characterization (tier A)

The LL-03 differential record and characterization goldens establish the fee, page, and payment behavior:

- Late days are calculated from the due date to `returnedOn` or today; up to two days late is waived, then 25 cents per day, capped at $10. Tests cover boundary days, cap, and returned-loan date behavior.
- `GET /fees/{id}` matches the characterized HTML; an unknown loan returns 404 with `<p>No such loan.</p>`. The browser fee page displays the same capped amount.
- Payment verifies the loan, then sends an empty-body `POST /charge?loan={id}` to the configured/default gateway URL. A gateway 200 maps to 200; other responses and I/O/interruption failures map to 502; unknown loans do not call the gateway. The API and `/ui/` flow retain separate paths.

**Verification and audit:** The initial verification (#90, PR #91) returned `blocked` after the default-order full suite lost a seeded loan in a live-server test; changed-code mutation could not collect the selected fee modules. The re-verification (#96, PR #97) passed after the test-isolation fix, including full suite and changed-code mutation (0.914). The independent audit (#114, PR #116) returned `complete` with no capability gaps or graph inconsistencies. It reviewed applicable quirk rulings and the payment-gateway design.

## Mutation (full run)

The archived full mutation score is 0.975 against a 0.8 threshold: 236 killed, 6 survived. Four survivors are outside the fees slice. The two fees survivors make internal `Fee` and `GatewayResponse` dataclasses mutable; the Auditor assessed them as equivalent for the observable contract because the fee/payment boundary does not mutate those values. They remain documented survivors.

## Capability coverage (gate 7)

All fees ledger entries are `migrated` and have target components and differential evidence.

| Capability | Target and evidence | Status |
|---|---|---|
| `fees.calculation` | `FeeApplication.fee_for`; fee golden; `tests/fees/test_fee_calculation.py` boundary and returned-date tests | `migrated` |
| `fees.page` | API/UI fee views, routes, and detail template; `tests/fees/test_endpoints.py` HTML, unknown-loan, browser payment, and seed-restoration tests | `migrated` |
| `integration.payment-gateway` | `FeeApplication.pay`, gateway protocol/adapter, repository, and composition; gateway golden and endpoint/failure tests | `migrated` |

## Human check

**Requested, not yet performed.** Compare legacy and target side by side using identical loan data, clock/date, requests, and gateway outcomes. Record the legacy and target observations for each:

1. An overdue loan: late-day count, fee amount in cents, displayed dollar amount, and legacy rounding/precision behavior.
2. A loan that is not overdue: calculated fee and its API/page presentation.
3. An unknown loan: exact status and response body, and whether either side contacts the gateway.
4. Paying a fee through the API and through the UI: each flow's request/interaction and success response or visible page update.
5. A failed payment gateway: non-200 response and I/O/interruption failure, including the resulting status/body or UI state. The target's 502 behavior follows the approved quirk ruling.
