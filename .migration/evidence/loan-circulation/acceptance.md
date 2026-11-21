# Loan circulation — acceptance evidence

- Slice: `loan-circulation` (#60)
- Acceptance run: [42752283868, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868), on commit `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`
- Archived result: `.migration/evidence/acceptance-runs/42752283868-1.json`; artifact retained through 2026-12-10
- This report uses the archived run; acceptance gates and mutation were not rerun.

## Acceptance evidence

| Result | Archived outcome |
|---|---|
| Source graph | Successful; 8 entry points, 6 reaching data |
| Target graph | Successful; 16 entry points, 12 reaching data |
| Build, idiom, and behavior | All workflow steps successful |
| CRAP | Maximum 7.0; threshold 30 |
| Full mutation | 0.920; 126 killed, 11 survived; threshold 0.8 |

The run's verified result is in the archive above. Its gate journal rows are retained in `.migration/evidence/runs/LC-ACCEPT.md`.

## Verification and audit history

| Work | Evidence | Finding |
|---|---|---|
| Initial LL-02 verification | #78, PR #79; `.migration/returns/LL-02.afs-verifier.yaml` at that landing | `changes-required`; lending and return use cases were coupled to Django |
| LL-02 re-verification | #84, PR #85; `.migration/returns/LL-02.afs-verifier.yaml` | `pass`; use cases depend on application-owned ports and characterized API/UI behavior was verified |
| Initial circulation audit | #94, PR #95; `.migration/returns/LC-AUDIT.afs-auditor.yaml` at that landing | `gaps-remain`; `loan.lend` and `loan.return-date` had misplaced target references |
| Ledger correction | PR #98 | Corrected the stale target references |
| Circulation re-audit | #100, PR #101; current `.migration/returns/LC-AUDIT.afs-auditor.yaml` | `complete`; all three circulation entries name existing target components |

## Circulation ledger

| Entry | Current status | Evidence summary |
|---|---|---|
| `loan.lend` | `migrated` | Tier-A characterization and LL-02 tests cover required/blank fields, 14-day due dates, escaped delimiters, API lending, and the new-loan UI |
| `loan.return` | `migrated` | Tier-A characterization and LL-02 tests cover successful return, unknown loans, repeated-return HTTP 409, and browser/HTMX return |
| `loan.return-date` | `migrated` | Tier-A characterization and LL-02 tests verify the first return date persists and a repeated return leaves it unchanged |

The re-audit reported no capability gaps. It did note a target-graph discrepancy: the graph maps `POST /loans` through the listing/read path, while the inspected view branches to lending and behavior tests verify loan creation. The audit classifies this as a graph-path inconsistency, not a missing capability. The full mutation run had 11 survivors; the final audit reviewed the route, method-guard, and form-model cases against behavior tests.

## Human side-by-side check — requested

Compare the legacy Lending Library against the target for each flow:

1. **API lending (`POST /loans`):** missing and blank member/ISBN field errors; for valid fields, the created loan record and response, including the 14-day due date and escaping of delimiter characters.
2. **API returning (`POST /loans/{id}/return`):** the first return succeeds and saves the return date; a repeat returns HTTP 409 and leaves that saved date unchanged.
3. **Browser forms:** `/ui/loans/new/` and `/ui/loans/{id}/return/`, comparing the available fields, successful flow, and validation/error behavior.

The human comparison remains requested. No human outcome or approval is recorded.
