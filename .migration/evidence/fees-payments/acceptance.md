# Fees and payments — acceptance evidence

- Slice: `fees-payments` · Epic: #62 · Acceptance ticket: LF-ACCEPT (#117)
- Acceptance run: [42912984554, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42912984554)
- Commit: `8f9a11640eef9801378f3db53a76903363c5e5b5`
- Archived result: `.migration/evidence/acceptance-runs/42912984554-1.json`
- Report date: 2026-11-21

## Acceptance run

The archived acceptance result is `passed`, with exit code 0, for the exact commit above. The source graph passed with 8 entry points and 6 reaching data; the target graph passed with 23 entry points, 18 reaching data, and 13 owned entry points (none unowned). Runtime, harness integrity, services, graph freshness, build, idiom, and the full test suite all exited 0. CRAP max was 7.0 (threshold 30). Full mutation scored 0.975 (threshold 0.8; 236 killed, 6 survived, 15 files).

These are results from the archived run, preserved in `.migration/evidence/acceptance-runs/42912984554-1.json` and the LF-AUDIT journal `.migration/evidence/runs/LF-AUDIT.md`. No acceptance gates or mutation were run for this ticket.

## Verification and audit

- **Initial verification, #90 / PR #91:** `blocked`; the full suite exposed test-isolation interference with the loan-catalog live-server browser test. The follow-up ticket addressed test isolation.
- **Re-verification, #96 / PR #97:** `pass`; the full default-order suite passed, and the verifier recorded a 0.914 changed-code mutation score.
- **Audit, #114 / PR #116:** `complete`; the independent auditor found no capability gaps or graph inconsistencies and reviewed the quirk rulings, test-first evidence, gateway design, and surviving mutants. Of the six full-run survivors, two fees mutants make internal `Fee` and `GatewayResponse` dataclasses mutable; the auditor assessed them as equivalent for the observable contract and documented that assessment.

## Ledger status

| Capability | Status | Evidence |
|---|---|---|
| `fees.calculation` | `migrated` | Differential characterization and fee-boundary tests; `.migration/ledger/fees.calculation.yaml` |
| `fees.page` | `migrated` | Differential API and UI/browser-flow tests; `.migration/ledger/fees.page.yaml` |
| `integration.payment-gateway` | `migrated` | Differential gateway request, response, and failure tests; `.migration/ledger/integration.payment-gateway.yaml` |

All three existing fees ledger entries are `migrated`, with target components and differential evidence. No ledger changes were needed.

## Human side-by-side check — requested

Compare the legacy application against the target using the same loan data, date/clock, request, and gateway outcome. Record the observed legacy and target values or responses side by side for each case:

1. **Overdue loan:** compare late-day count, fee amount, and displayed amount, including the amount/rounding behavior.
2. **Loan that is not overdue:** compare the calculated fee and its API/page presentation.
3. **Unknown loan:** compare the exact status and response body, and whether either implementation calls the gateway.
4. **Fee payment through the API and UI:** compare each request/interaction and its success response or visible page update.
5. **Payment gateway failure:** compare the response to a non-200 gateway result and to an I/O/interruption failure, including the resulting status/body or UI state.

The target's interruption-to-502 behavior follows the approved quirk ruling. No human comparison or sign-off has been recorded; this request does not mark the check passed.
