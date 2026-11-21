# Loan circulation — slice acceptance

- **Epic:** martins-vds/ai-factory-synthetic-target#60
- **Tickets:** LL-02 (#61), its sub-issues #78 and #84, LC-AUDIT (#94), LC-REAUDIT (#100), and LC-ACCEPT (#108)
- **Audited commit:** `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`
- **Acceptance run:** [42752283868, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868)
- **Archived result:** `.migration/evidence/acceptance-runs/42752283868-1.json`

## Gate results

The accepted run passed without rerunning gates or mutation in this session.

| Area | Result |
|---|---|
| Source graph | 8 entry points, 6 reaching data |
| Target graph | 16 entry points, 12 reaching data |
| Build | Both build steps passed |
| Idiom | Ruff check and format check passed |
| Behavior | Full pytest suite passed |
| CRAP | Maximum 7.0; threshold 30 |
| Full mutation | Score 0.920; 126 killed, 11 survived; threshold 0.8 |

The gate and mutation archive is the verified result for commit `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`.

## Verification and audit

- LL-02 (#61) landed in PR #75.
- Initial verification (#78, PR #79) identified the Django coupling finding.
- Re-verification (#84, PR #85) passed after the ports/adapters remediation.
- LC-AUDIT (#94, PR #95) reviewed the circulation capabilities and returned `gaps-remain` for two misplaced ledger references.
- PR #98 corrected the ledger references.
- LC-REAUDIT (#100, PR #101) returned `complete`: all three ledger capabilities now name current implementation components and no ledger gaps remain.

## Ledger status

| Capability | Status | Verification |
|---|---|---|
| `loan.lend` | `migrated` | Tier A differential characterization; lending endpoint, browser, HTMX, blank-field, and delimiter-escaping behavior is covered. |
| `loan.return` | `migrated` | Tier A differential characterization; first return, repeat 409, not-found 404, browser, and HTMX behavior is covered. |
| `loan.return-date` | `migrated` | Tier A differential characterization; first-return persistence and preservation of the original repeated-return date are covered. |

## Human check

Human check is **requested**. Compare the legacy Lending Library against the target side by side:

1. Lending through the API: reject missing or blank member and ISBN fields; on valid lending, use today as the loan date and 14 days for the due date; verify the returned and exported record escapes delimiters.
2. Returning through the API: verify a first return succeeds and records today's date; repeat the same return and verify HTTP 409, `already returned`, and that the saved first return date is unchanged.
3. Browser flows: create a loan at `/ui/loans/new/`, including blank-field error handling and HTMX behavior; return a loan through the return form, including not-found and repeated-return handling.

This request does not set a passed or approved outcome. ADR-0031 requires the human approver's independent review.
