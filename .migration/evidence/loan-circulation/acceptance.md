# Slice loan-circulation — acceptance evidence

- Tickets: LL-02 (#61), #78, #84, #94, #100, and LC-ACCEPT (#108) · Slice: `loan-circulation` · Date: 2026-11-10 (acceptance run; report prepared 2026-11-21)
- Acceptance run: [42752283868, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868), passed on commit `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`
- Archived result: `.migration/evidence/acceptance-runs/42752283868-1.json` (artifact retained through 2026-12-10)
- Prior audit evidence: `.migration/evidence/loan-circulation/report.md`; re-audit return: `.migration/returns/LC-AUDIT.afs-auditor.yaml`

The archived result is for the same commit audited by LC-REAUDIT. The coordinator did not rerun acceptance gates or mutation.

| Gate | Result |
|---|---|
| Source graph | Pass; 8 entry points, 6 reaching data |
| Target graph | Pass; 16 entry points, 12 reaching data |
| Build, idiom, and behavior | All planned steps passed |
| CRAP | Maximum 7.0; threshold 30 |
| Full mutation | 0.920; 126 killed, 11 survived; threshold 0.8 |

## Verification and audit history

| Work | Evidence | Outcome |
|---|---|---|
| LL-02 implementation | #61, PR #75; `.migration/returns/LL-02.afs-migrator.yaml` | Merged; implements lending and returning |
| Initial LL-02 verification | #78, PR #79; verifier return at that landing | `changes-required`; application policy was coupled to Django |
| Follow-up LL-02 verification | #84, PR #85; `.migration/returns/LL-02.afs-verifier.yaml` | `pass`; ports remediation and behavior were verified |
| Initial circulation audit | #94, PR #95; auditor return at that landing | `gaps-remain`; `loan.lend` and `loan.return-date` had misplaced target references |
| Ledger correction | PR #98 | Corrected the stale target references |
| Re-audit | #100, PR #101; `.migration/returns/LC-AUDIT.afs-auditor.yaml` | `complete`; no capability gaps remain |

## Capability coverage

All three circulation entries remain `migrated`, with differential verification and target tests in their ledgers.

| Capability | Target components | Evidence and status |
|---|---|---|
| `loan.lend` | `LoanForm`, `LoanApplication.lend`, `loan_collection`, `loan_lend_page` | LL-02 tests cover required fields, 14-day due dates, delimiter escaping, API lending, and the new-loan UI. `migrated`. |
| `loan.return` | `loan_return`, `loan_return_page`, `loans.urls` | LL-02 tests cover successful return, unknown loans, repeated-return `409`, and browser/HTMX return. `migrated`. |
| `loan.return-date` | `DjangoLoanRepository.mark_returned`, `LoanApplication.return_loan` | LL-02 tests cover saving the first return date and preserving it after a repeated return. `migrated`. |

The re-audit found no ledger gaps. It noted a target-graph path inconsistency: the accepted graph maps `POST /loans` through the listing/read path, while the inspected view branches to lending and behavior tests verify loan creation. This remains an under-described graph path, not a missing capability. The full mutation run had 11 survivors; the final audit reviewed the route, method-guard, and form-model cases against behavior tests.

## Human side-by-side check — requested

Compare legacy behavior with the target, recording the observed behavior on each side and the approved differences:

1. **API lending:** required member and ISBN fields, the 14-day due date, and delimiter escaping in the resulting loan record. In particular, check the approved blank-field rejection and delimiter-escaping changes against the legacy behavior.
2. **Returns:** the first return succeeds and saves its date; a repeat return answers `409` and leaves the saved date unchanged, as the approved change from the legacy overwrite behavior.
3. **Browser forms:** `/ui/loans/new/` and `/ui/loans/{id}/return/`, including their successful submissions and validation/error behavior.

The human check is requested and remains pending. No pass or approval is recorded.
