# Fees and payments — acceptance evidence

- Slice: `fees-payments` · Epic: #62 · Acceptance ticket: LF-ACCEPT (#117)
- Acceptance run: [42912984554, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42912984554)
- Commit: `8f9a11640eef9801378f3db53a76903363c5e5b5`
- Archived result: `.migration/evidence/acceptance-runs/42912984554-1.json`

## Acceptance run

The archived result is `passed` for the specified commit. The source and target graphs passed: source has 8 entry points and 6 reaching data; target has 23 entry points, 18 reaching data, and 13 owned with none unowned. Build, idiom, and the full test suite passed. CRAP maximum is 7.0 (threshold 30). Full mutation is 0.975 (threshold 0.8; 236 killed, 6 survived). The gate evidence is preserved in `.migration/evidence/runs/LF-AUDIT.md`; this coordinator did not rerun gates or mutation.

## Characterization, verifications, and audit

Characterization is tier A. The existing detailed evidence in `.migration/evidence/fees-payments/report.md` records fee boundaries, API and UI behavior, gateway requests and responses, quirk rulings, and the six surviving mutants.

- **Implementation, #63 / PR #88:** LL-03 migrated the three fees capabilities; its return records passing build, behavior, idiom, CRAP, mutation, and regression gates.
- **Initial verification, #90 / PR #91:** verdict `blocked`; the full suite failed because seed data was lost during test isolation. The verifier recorded the failure rather than claiming a pass.
- **Re-verification, #96 / PR #97:** verdict `pass`; the test-isolation fix restored the default-order full suite, and build, behavior, idiom, CRAP, changed-code mutation (0.914), and regression gates passed.
- **Audit, #114 / PR #116:** verdict `complete`, with no capability gaps or graph inconsistencies. The independent audit reviewed the quirk rulings and payment-gateway design. The two full-run survivors in this slice make the internal `Fee` and `GatewayResponse` dataclasses mutable; they were assessed as equivalent for the observable contract and remain documented.

## Ledger status

| Capability | Status | Evidence |
|---|---|---|
| `fees.calculation` | `migrated` | Differential characterization and fee-boundary tests; `.migration/ledger/fees.calculation.yaml` |
| `fees.page` | `migrated` | Differential API and UI/browser-flow tests; `.migration/ledger/fees.page.yaml` |
| `integration.payment-gateway` | `migrated` | Differential gateway request/response and failure tests; `.migration/ledger/integration.payment-gateway.yaml` |

All three entries have target components and differential evidence; their existing ledger statuses are consistent with the accepted implementation and independent audit.

## Human side-by-side check — requested

Compare legacy and target using identical loan data, clock/date, request, and gateway outcome. For each case, record the observed legacy and target values or responses:

1. **Overdue loan:** compare due date, late-day count, fee amount in cents, displayed dollar amount, and rounding/precision.
2. **Not-overdue loan:** compare the calculated fee and its API and page presentation.
3. **Unknown loan:** compare the exact API and UI status/body and whether either side contacts the gateway.
4. **Fee payment through API and UI:** compare the API request/response and the UI interaction/result, including the gateway request and successful outcome.
5. **Failed gateway payment:** compare non-200 and I/O/interruption failures, including API status/body and the resulting UI state.

No human side-by-side check has been reported yet. The operator's check remains requested; this report does not mark it passed.
