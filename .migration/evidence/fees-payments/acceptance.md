# Fees and payments — acceptance evidence

- Slice: `fees-payments` · Epic: #62 · Acceptance ticket: LF-ACCEPT (#117)
- Acceptance run: [42912984554, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42912984554)
- Commit: `8f9a11640eef9801378f3db53a76903363c5e5b5`
- Archived result: `.migration/evidence/acceptance-runs/42912984554-1.json`

## Acceptance run

The archived result is `passed` for the specified commit. Source and target graphs passed: source has 8 entry points and 6 reaching data; target has 23 entry points, 18 reaching data, and 13 owned entry points with none unowned. Build, idiom, and full test suite passed. CRAP maximum is 7.0 (threshold 30). Full mutation score is 0.975 (threshold 0.8; 236 killed, 6 survived). These results are from the archived run and its verified provenance recorded in `.migration/evidence/runs/LF-AUDIT.md`. No acceptance gates or mutation were run in this session.

## Verifications and audit

- **Initial verification, #90 / PR #91:** `blocked`. The full suite failed because the live-server loan-catalog browser test could not find a seed loan after test isolation was lost; changed-code mutation did not produce a score because mutmut could not collect the selected fee modules.
- **Re-verification, #96 / PR #97:** `pass`. The test-isolation fix restored the default-order full suite; build, behavior, idiom, CRAP, changed-code mutation (0.914), and regression gates passed.
- **Audit, #114 / PR #116:** `complete`. The independent audit found no capability gaps or graph inconsistencies across the three fees ledger entries and reviewed the quirk rulings and payment-gateway design. Six full-run mutants survived; two in the fees slice make internal `Fee` and `GatewayResponse` dataclasses mutable and were assessed as equivalent for the observable contract.

## Ledger status

| Capability | Status | Evidence |
|---|---|---|
| `fees.calculation` | `migrated` | Differential characterization and fee-boundary tests; `.migration/ledger/fees.calculation.yaml` |
| `fees.page` | `migrated` | Differential API and UI/browser-flow tests; `.migration/ledger/fees.page.yaml` |
| `integration.payment-gateway` | `migrated` | Differential gateway request/response and failure tests; `.migration/ledger/integration.payment-gateway.yaml` |

All three slice entries are already `migrated`, with target components and differential evidence; the independent audit found no gaps.

## Human side-by-side check — requested

Using the same loan data, date/clock, request, and gateway outcome, compare legacy against target and record both observations for each case:

1. **Overdue loan:** late-day count, fee amount, displayed dollars, and rounding/precision.
2. **Not-overdue loan:** calculated fee and API/page presentation.
3. **Unknown loan:** exact HTTP status and response body, and whether either implementation calls the gateway.
4. **Payment through API and UI:** request/interaction and the success response or visible page update.
5. **Gateway failure:** non-200 response and I/O/interruption failure, including the resulting status/body or UI state.

The target's HTTP 502 handling follows the approved quirk ruling. No operator side-by-side result has been recorded. Keep the human check requested; this report does not mark it passed or approve the slice.
