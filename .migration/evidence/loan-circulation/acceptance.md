# Loan circulation — acceptance evidence

- Slice: Loan circulation (#60)
- Acceptance ticket: LC-ACCEPT (#108), PR #109
- Implementation and review tickets: LL-02 (#61), verifier #78 and re-verifier #84, audit #94 and re-audit #100
- Acceptance commit: `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`
- Acceptance run: [42752283868, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868), on `main`; result archived at `.migration/evidence/acceptance-runs/42752283868-1.json`
- Recorded: 2026-11-21

The GitHub Actions run is complete with conclusion `success` for the specified commit and attempt. The archived result has `status: passed`; all 15 planned run steps passed. No acceptance gate or mutation command was run again for this report.

## Gates

| Gate | Archived result | Notes |
|---|---|---|
| Runtime, harness integrity, services | Passed | Runtime and services healthy; installed harness verified |
| Source and target graphs | Passed | Freshness passed; source: 8 entry points, 6 reaching data; target: 16 entry points, 12 reaching data |
| Build | Passed | `python -m compileall -q src`; `python manage.py check` |
| Idiom | Passed | Ruff check and format check |
| Behavior | Passed | Full `pytest -q` suite |
| CRAP | Passed | Maximum 7.0 against threshold 30 |
| Full mutation | Passed | Score 0.920 against threshold 0.8; 126 killed, 11 survived |

The gate-by-gate run output and unchanged artifact are retained in the archive above. The existing detailed audit report is `.migration/evidence/loan-circulation/report.md`.

## Implementation and reviews

- LL-02 (#61) landed in PR #75. The first verifier, #78 / PR #79, recorded `changes-required`; its port-and-adapter finding was addressed. Re-verifier #84 / PR #85 returned `pass`.
- LC-AUDIT (#94 / PR #95) found two misplaced ledger component references. PR #98 corrected them. LC-REAUDIT (#100 / PR #101) returned `complete` with no ledger gaps.
- The re-audit retains a target-graph path inconsistency for `POST /loans`: the graph describes a read path while the inspected POST branch lends a book. The audit classifies this as graph under-description, not a missing capability.

## Capability coverage

| Ledger entry | Status | Target components | Evidence |
|---|---|---|---|
| `loan.lend` | `migrated` | `LoanForm`, `LoanApplication.lend`, `loan_collection`, `loan_lend_page` | Tier-A characterization; acceptance behavior tests for API and browser lending, required/blank fields, 14-day due date, and escaped exports; LC-REAUDIT |
| `loan.return` | `migrated` | `loan_return`, `loan_return_page`, `urls` | Tier-A characterization; acceptance behavior tests for API and browser return, unknown loans, and repeated returns; LC-REAUDIT |
| `loan.return-date` | `migrated` | `DjangoLoanRepository.mark_returned`, `LoanApplication.return_loan` | Tier-A characterization; acceptance behavior and service tests for first and repeated returns; LC-REAUDIT |

All three entries are `migrated`, and the re-audit reports zero capability gaps. The approved fix rulings relevant to these entries are #39 (blank required fields), #41 (repeated return), and #43 (delimiter escaping).

## Human side-by-side check — requested

Compare the legacy API with the target API at `POST /loans` and `POST /loans/{id}/return`:

1. Submit missing and blank member/ISBN values. Confirm required-field behavior and explicitly compare the approved #39 divergence: the legacy accepts blank strings, while the target rejects them.
2. Lend a valid book. Compare the created loan, response format, dates, and due date (14 calendar days after lending).
3. Export values containing semicolons or line breaks. Compare the legacy raw-delimiter output with the target's escaped output under approved ruling #43.
4. Return a loan once, then return it again. Compare the first persisted return date and the repeat response/date: the legacy overwrites the date, while the target responds `409` and preserves the original date under approved ruling #41. Also compare the unknown-loan `404` response.
5. Exercise the target browser forms at `/ui/loans/new/` and `/ui/loans/{id}/return/`: compare validation, success/error states, and persisted outcomes with the corresponding legacy API behavior. The browser routes are target-specific; do not treat them as legacy screens.

This check is requested only. No human result or approval is recorded here.
