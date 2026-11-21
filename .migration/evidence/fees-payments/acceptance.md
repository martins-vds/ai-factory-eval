# Fees and payments — acceptance evidence

- Slice: `fees-payments` · Epic: martins-vds/ai-factory-synthetic-target#62 · Acceptance ticket: LF-ACCEPT (#117)
- Acceptance run: [42912984554, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42912984554)
- Commit: `8f9a11640eef9801378f3db53a76903363c5e5b5`
- Archived result: `.migration/evidence/acceptance-runs/42912984554-1.json`
- Evidence date: 2026-11-21

## Gates

The archived result is `passed` for the exact commit above. The results below are from the verified acceptance run and the preserved journal at `.migration/evidence/runs/LF-AUDIT.md`; no gates or mutation were rerun for this acceptance.

| Gate | Command | Exit | Notes |
|---|---|---:|---|
| Runtime | `check_runtime.py` | 0 | Python 3.13 |
| Harness integrity | `check_installed.py` | 0 | Installed pins valid |
| Services | `afs-services check` | 0 | Test services healthy |
| Graph freshness | `check_graph_fresh.py --require source,target` | 0 | Both graphs fresh |
| Source graph | `graph_gate.py --side source --require-graph` | 0 | 8 entry points; 6 reaching data |
| Target graph | `graph_gate.py --side target --require-graph --enforce-ownership` | 0 | 23 entry points; 18 reaching data; 13 owned, none unowned |
| Build | `python -m compileall -q src`; `python manage.py check` | 0 | Both passed |
| Idiom | `ruff check src config manage.py tests`; `ruff format --check src config manage.py tests` | 0 | Both passed |
| Tests | `pytest -q` | 0 | Full suite passed |
| CRAP | Coverage pytest, `lizard --csv src`, then `crap.py ... --max 30` | 0 | Maximum 7.0; threshold 30 |
| Full mutation | `python .migration/harness/tools/afs-mutation --all` | 0 | 0.975; threshold 0.8; 236 killed, 6 survived, 15 files |

## Characterization (tier A)

The independent audit verified the LL-03 differential evidence against the legacy goldens and tests: the fee uses the characterized two-day waiver, 25 cents per late day, and $10 cap; returned loans use `returned_on`; the API fee page and unknown-loan response match; and payment uses the characterized gateway request, with the audited success and failure behavior. Details and case evidence remain in `.migration/evidence/fees-payments/report.md` and `.migration/evidence/runs/LL-03.md`.

## Mutation (full run)

The full run scored 0.975 against the 0.8 threshold (236 killed, 6 survived). Four survivors are outside the fees slice. The two fees survivors make `Fee` and `GatewayResponse` mutable; the auditor assessed them as equivalent for the observable contract because no path mutates either value. They remain documented, not suppressed.

## Ticket status and audit

- **LL-03 (#63):** landed in PR #88.
- **Initial verification (#90):** PR #91 returned `blocked` after the default-order suite failed because seed loans were lost during a live-server test; changed-code mutation could not collect the selected fee modules.
- **Re-verification (#96):** PR #97 returned `pass`; the test-isolation fix restored the full suite, and the behavior, build, idiom, CRAP, regression, and changed-code mutation gates passed (mutation 0.914).
- **LF-AUDIT (#114):** PR #116 returned `complete`, with no capability gaps or graph inconsistencies.
- **LF-ACCEPT (#117):** reconciled as completed with this acceptance PR.

## Capability coverage (gate 7)

| Capability | Target components | Status | Evidence |
|---|---|---|---|
| `fees.calculation` | `FeeApplication.fee_for`, `fee_detail`, `fee_page` | `migrated` | `.migration/ledger/fees.calculation.yaml`; `tests/fees/test_fee_calculation.py`; fee golden; `.migration/evidence/runs/LL-03.md` |
| `fees.page` | `fee_detail`, `fee_page`, fee routes and detail template | `migrated` | `.migration/ledger/fees.page.yaml`; `tests/fees/test_endpoints.py`; browser flow; `.migration/evidence/runs/LL-03.md` |
| `integration.payment-gateway` | `FeeApplication.pay`, `HttpPaymentGateway`, `DjangoFeeLoanRepository`, API/UI payment views | `migrated` | `.migration/ledger/integration.payment-gateway.yaml`; gateway golden; endpoint/gateway tests; `.migration/evidence/runs/LL-03.md` |

All three slice entries have target components and differential evidence. Their existing `migrated` statuses are consistent with the accepted implementation and independent audit. The auditor found no coverage gaps or graph inconsistencies.

## Human side-by-side check — requested

Compare the legacy application against the target using the same loan data, date/clock, request, and gateway outcome. For each case, record what the legacy does and what the target does:

1. **Overdue loan:** compare late-day count, fee amount, and displayed dollar amount, including the legacy's rounding or precision behavior.
2. **Loan that is not overdue:** compare the calculated fee and its API/page presentation.
3. **Unknown loan:** compare the exact status and response body, and whether either side contacts the gateway.
4. **Payment through the API and UI:** compare the respective request/interaction and the success response or visible page update.
5. **Failed payment gateway:** compare a non-200 response and an I/O/interruption failure, including the resulting status/body or UI state. Check that the target's 502 behavior and preserved interruption cause follow the approved quirk ruling.

No human side-by-side result has been reported. The check remains requested; this report does not mark it passed or approve the slice.
