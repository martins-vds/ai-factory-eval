# Loan circulation — acceptance

- Slice: `loan-circulation` (#60)
- Acceptance run: [42752283868, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868)
- Executed commit: `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`
- Archived result: `.migration/evidence/acceptance-runs/42752283868-1.json`
- The gates and mutation were not rerun in this session.

## Archived run results

| Result | Outcome |
|---|---|
| Source graph | 8 entry points, 6 reaching data; passed |
| Target graph | 16 entry points, 12 reaching data; passed |
| Build, idiom, and behavior | Passed |
| CRAP | Maximum 7.0; threshold 30 |
| Full mutation | 0.920; 126 killed, 11 survived; threshold 0.8 |

## Verification and audit history

- LL-02 initial verification: #78, PR #79; `changes-required` for application-policy/framework coupling.
- LL-02 re-verification: #84, PR #85; `pass` after the ports/adapters remediation.
- LC-AUDIT: #94, PR #95; initially found two misplaced ledger references.
- LC-REAUDIT: #100, PR #101; re-audit verdict `complete` after PR #98 corrected the ledger references.
- The re-audit found no remaining ledger capability gaps.

## Ledger status

| Entry | Status | Evidence |
|---|---|---|
| `loan.lend` | `migrated` | Tier-A characterization and LL-02 tests cover required fields, 14-day due date, delimiter escaping, API lending, and the `/ui/loans/new/` flow. |
| `loan.return` | `migrated` | Tier-A characterization and LL-02 tests cover first return, missing loans, repeat return `409`, and browser/HTMX return. |
| `loan.return-date` | `migrated` | Tier-A characterization and LL-02 tests verify that the first return date is saved and repeated returns preserve it. |

The final audit retained the target-graph `POST /loans` path inconsistency as a graph discrepancy, not a missing circulation capability.

## Human check

The human side-by-side check is requested. Compare legacy against target:

1. Lending through the API: required member and ISBN fields, the 14-day due date, and delimiter escaping in the loan record.
2. Returning: the first return succeeds and saves its date; a repeat return answers `409` and leaves the saved date unchanged.
3. The `/ui/loans/new/` lending form and `/ui/loans/{id}/return/` return form, including success and validation/error behavior.

No pass or approval is recorded in this acceptance.
