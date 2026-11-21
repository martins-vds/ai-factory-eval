# Loan circulation — acceptance

- Slice: `loan-circulation` (#60)
- Acceptance run: [42752283868, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868), successful on commit `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`
- Archived result: `.migration/evidence/acceptance-runs/42752283868-1.json` (artifact retained through 2026-12-10)
- Run journal: `.migration/evidence/runs/LC-ACCEPT.md`

No acceptance gates or mutation were rerun for this report. The archived result is for the specified commit and attempt; GitHub records the workflow conclusion as successful.

## Acceptance run

| Gate | Result |
|---|---|
| Source graph | Passed; 8 entry points, 6 reaching data |
| Target graph | Passed; 16 entry points, 12 reaching data |
| Build | All steps passed |
| Idiom | All steps passed |
| Behavior | Full test suite passed |
| CRAP | Maximum 7.0; threshold 30 |
| Full mutation | 0.920; 126 killed, 11 survived; threshold 0.8 |

## Verification and audit history

| Work | Evidence | Outcome |
|---|---|---|
| Initial LL-02 verification | #78, PR #79; `.migration/returns/LL-02.afs-verifier.yaml` at that landing | `changes-required`; application use cases were coupled to Django and the concrete ORM repository |
| Follow-up LL-02 verification | #84, PR #85; `.migration/returns/LL-02.afs-verifier.yaml` | `pass`; ports remediation and lending/return behavior were verified |
| Initial circulation audit | #94, PR #95; `.migration/returns/LC-AUDIT.afs-auditor.yaml` at that landing | `gaps-remain`; `loan.lend` and `loan.return-date` had misplaced target references |
| Re-audit | #100, PR #101, after ledger fix PR #98; current `.migration/returns/LC-AUDIT.afs-auditor.yaml` | `complete`; all three circulation ledger entries name existing implementation components |

## Circulation ledger

| Entry | Status | Evidence |
|---|---|---|
| `loan.lend` | `migrated` | Tier-A characterization and LL-02 tests cover required fields, 14-day due date, delimiter escaping, API lending, and the new-loan UI |
| `loan.return` | `migrated` | Tier-A characterization and LL-02 tests cover successful return, missing loans, repeat-return `409`, and browser/HTMX return |
| `loan.return-date` | `migrated` | Tier-A characterization and LL-02 tests verify the first return date is saved and repeat returns leave it unchanged |

The final audit found no capability gaps. It noted one target-graph path inconsistency: the accepted graph maps `POST /loans` through the listing/read path, while the inspected view branches to lending and tests verify loan creation. This was reported as a graph-path inconsistency, not a missing capability. The full mutation run had 11 survivors; the final audit reviewed the route, method-guard, and form-model cases against behavior tests.

## Human side-by-side check — requested

Compare the legacy behavior with the target behavior:

1. **Lending through the API:** missing or blank member and ISBN fields are rejected; valid lending uses the 14-day due date; delimiter characters in the resulting loan record are escaped.
2. **Returning through the API:** the first return succeeds and saves its date; a repeat return answers `409` and leaves the saved return date unchanged.
3. **Target browser forms:** exercise `/ui/loans/new/` and `/ui/loans/{id}/return/`, including their validation, success, and error behavior. Compare their observable outcomes and persisted effects with the corresponding legacy API behavior; the legacy boundary is API-based.

The human check remains requested. No sign-off or approval is recorded here.
