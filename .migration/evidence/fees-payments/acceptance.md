# Fees and payments — acceptance evidence

- Slice: `fees-payments` · Epic: #62 · Acceptance ticket: LF-ACCEPT (#117)
- Acceptance run: [42912984554, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42912984554)
- Commit: `8f9a11640eef9801378f3db53a76903363c5e5b5`
- Archived result: `.migration/evidence/acceptance-runs/42912984554-1.json`

## Acceptance run

The archived result is passed for the exact commit above, and GitHub reports the workflow and all three jobs successful. Source and target graphs both pass: source has 8 entry points and 6 reaching data; target has 23 entry points, 18 reaching data, and 13 owned with none unowned. Build, idiom, and the full test suite pass. CRAP maximum is 7.0 (threshold 30). Full mutation is 0.975 (threshold 0.8; 236 killed, 6 survived). These acceptance-gate rows are preserved in `.migration/evidence/runs/LF-AUDIT.md` and copied to this ticket's journal; this coordinator did not rerun gates or mutation.

## Characterization, verifications, and audit

Characterization is tier A. The existing detailed evidence in `.migration/evidence/fees-payments/report.md` records fee boundaries, API and UI behavior, gateway requests and responses, quirk rulings, and the six surviving mutants.

- **Implementation, #63 / PR #88:** LL-03 migrated the three fees capabilities; its return records passing build, behavior, idiom, CRAP, mutation, and regression gates.
- **Initial verification, #90 / PR #91:** verdict `blocked`. The full suite failed because the live-server loan-catalog browser test could not find a seed loan after test isolation was lost; changed-code mutation did not produce a score because mutmut could not collect the selected fee modules. The verifier recorded this rather than claiming a pass.
- **Re-verification, #96 / PR #97:** verdict `pass`. The test-isolation fix restored the default-order full suite; build, behavior, idiom, CRAP, changed-code mutation (0.914), and regression gates passed.
- **Audit, #114 / PR #116:** verdict `complete`, with no capability gaps or graph inconsistencies. The independent audit reviewed the quirk rulings and payment-gateway design. Of the six full-run survivors, the two in this slice make the internal `Fee` and `GatewayResponse` dataclasses mutable; they were assessed as equivalent for the observable contract and remain documented.

## Ledger status

| Capability | Status | Evidence |
|---|---|---|
| `fees.calculation` | `migrated` | Differential characterization and fee-boundary tests; `.migration/ledger/fees.calculation.yaml` |
| `fees.page` | `migrated` | Differential API and UI/browser-flow tests; `.migration/ledger/fees.page.yaml` |
| `integration.payment-gateway` | `migrated` | Differential gateway request/response and failure tests; `.migration/ledger/integration.payment-gateway.yaml` |

All three entries have target components and differential evidence; their existing ledger statuses are consistent with the accepted implementation and independent audit.

## Human check — requested

Compare legacy and target side by side using identical loan data, clock/date, request, and gateway outcome. For each case, record the observed legacy and target values or responses:

1. An overdue loan: compare late-day count, fee amount in cents, displayed dollar amount, and rounding/precision.
2. A loan that is not overdue: compare the calculated fee and its API/page presentation.
3. An unknown loan: compare the exact status and response body, and whether either side contacts the gateway.
4. Paying a fee through the API and through the UI: compare each request/interaction and the success response or visible page update.
5. A failed payment gateway: compare a non-200 response and an I/O/interruption failure, including the resulting status/body or UI state.

No human side-by-side check has been reported yet. The slice awaits that operator check; this report does not mark it passed.
