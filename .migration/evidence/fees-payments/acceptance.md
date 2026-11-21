# Fees and payments — acceptance evidence

- Slice: `fees-payments` · Epic: #62 · Acceptance ticket: LF-ACCEPT (#117)
- Acceptance run: [42912984554, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42912984554)
- Commit: `8f9a11640eef9801378f3db53a76903363c5e5b5`
- Archived result: `.migration/evidence/acceptance-runs/42912984554-1.json`

## Acceptance run

The archived result passed for the exact commit above. The source and target graphs passed: source has 8 entry points and 6 reaching data; target has 23 entry points, 18 reaching data, and 13 owned with none unowned. Build, idiom, and the full test suite passed. CRAP maximum is 7.0 (threshold 30). Full mutation score is 0.975 (threshold 0.8; 236 killed, 6 survived). These results are from the archived acceptance run recorded in `.migration/evidence/runs/LF-ACCEPT.md`; the coordinator did not rerun gates or mutation.

## Verifications and audit

- **Initial verification, #90 / PR #91:** `blocked`. The full suite failed in an existing live-server loan-catalog browser test after its seed-loan isolation was lost; changed-code mutation did not produce a score because mutmut could not collect the selected fee modules.
- **Re-verification, #96 / PR #97:** `pass`. The test-isolation fix restored the default-order full suite; build, behavior, idiom, CRAP, changed-code mutation (0.914), and regression gates passed.
- **Audit, #114 / PR #116:** `complete`. The independent audit found no capability gaps or graph inconsistencies across the three fees ledger entries and reviewed the quirk rulings, test-first evidence, and payment-gateway design. Six full-run mutants survived; two in this slice make the internal `Fee` and `GatewayResponse` dataclasses mutable and were assessed as equivalent for the observable contract. They remain documented survivors.

## Ledger status

| Capability | Status | Evidence |
|---|---|---|
| `fees.calculation` | `migrated` | Differential characterization and fee-boundary tests; `.migration/ledger/fees.calculation.yaml` |
| `fees.page` | `migrated` | Differential API and UI/browser-flow tests; `.migration/ledger/fees.page.yaml` |
| `integration.payment-gateway` | `migrated` | Differential gateway request/response and failure tests; `.migration/ledger/integration.payment-gateway.yaml` |

Each slice entry has target components and differential evidence. The existing ledger statuses are consistent with the accepted implementation and independent audit.

## Human check — requested

Compare the legacy application and target side by side using the same loan data, clock/date, request, and gateway outcome. Record the observed legacy and target values or responses for each case:

1. An overdue loan: compare late-day count, fee amount in cents, displayed dollar amount, and the legacy rounding/precision behavior.
2. A loan that is not overdue: compare the calculated fee and page/API presentation.
3. An unknown loan: compare the exact status and response body, and confirm whether either side contacts the gateway.
4. Paying a fee through the API and through the UI: compare the request or interaction and the success response or visible page update.
5. A failed payment gateway: compare a non-200 response and an I/O/interruption failure, including the resulting status/body or UI state. The target's 502 handling follows the approved quirk ruling.

No human side-by-side check has been reported yet. The check remains requested; this report does not mark it passed.
