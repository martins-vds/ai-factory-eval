# Loan circulation — acceptance

- Slice: `loan-circulation` (#60)
- Acceptance run: [42752283868, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868), passed on commit `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`
- Archived result: `.migration/evidence/acceptance-runs/42752283868-1.json`
- No acceptance gates or mutation work was rerun for this acceptance.

## Run results

| Result | Outcome |
|---|---|
| Source graph | Pass: 8 entry points, 6 reaching data |
| Target graph | Pass: 16 entry points, 12 reaching data |
| Build and idiom | All build and idiom steps passed |
| Behavior tests | `pytest -q` passed |
| CRAP | Maximum 7.0; threshold 30 |
| Full mutation | 0.920; 126 killed, 11 survived; threshold 0.8 |

## Verification and audit history

| Work | Evidence | Outcome |
|---|---|---|
| LL-02 implementation | #61, PR #75, `.migration/returns/LL-02.afs-migrator.yaml` | Implementation landed |
| Initial verification | #78, PR #79, `.migration/returns/LL-02.afs-verifier.yaml` | `changes-required`; use cases retained Django/ORM dependencies |
| Re-verification | #84, PR #85, `.migration/returns/LL-02.afs-verifier.yaml` | `pass`; ports remediation and behavior were verified |
| Initial audit | #94, PR #95, `.migration/returns/LC-AUDIT.afs-auditor.yaml` | Found two misplaced ledger references |
| Re-audit | #100, PR #101, `.migration/returns/LC-AUDIT.afs-auditor.yaml` | `complete`; the ledger references and remaining evidence were accepted |

## Ledger status

| Ledger entry | Status | Characterization |
|---|---|---|
| `loan.lend` | `migrated` | Tier A; required fields, 14-day due date, delimiter escaping, API lending, and browser lending are evidenced |
| `loan.return` | `migrated` | Tier A; first return, repeat `409`, unknown loan `404`, and browser/HTMX return are evidenced |
| `loan.return-date` | `migrated` | Tier A; first return persists today's date and repeat return preserves the original date |

The re-audit found no remaining capability gaps.

## Human side-by-side check — requested

Compare the legacy Lending Library against the target:

1. **Lending through the API:** require a member and ISBN; a valid lending request creates a loan with the 14-day due date; delimiters in returned/recorded loan fields are escaped.
2. **Returning:** a first return succeeds and saves its date; a repeat return answers `409` and leaves the saved date unchanged.
3. **Browser forms:** compare `/ui/loans/new/` and `/ui/loans/{id}/return/`, including success, validation, not-found, and repeat-return behavior.

No pass or approval is recorded. The human check is requested and remains pending.
