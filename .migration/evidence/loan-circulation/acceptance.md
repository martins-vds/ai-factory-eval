# Loan circulation — acceptance

- Epic: Loan circulation (#60)
- Tickets: LL-02 (#61), verifier #78/#84, LC-AUDIT (#94), LC-REAUDIT (#100), LC-ACCEPT (#108)
- Executed commit: `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`
- Acceptance run: [42752283868, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868)
- Archived result: `.migration/evidence/acceptance-runs/42752283868-1.json`
- Result: **passed**

## Gates

| Gate | Result | Evidence |
|---|---|---|
| Source graph | Pass | 8 entry points, 6 reaching data |
| Target graph | Pass | 16 entry points, 12 reaching data |
| Build | Pass | `compileall` and `manage.py check` |
| Idiom | Pass | Ruff check and format check |
| Tests | Pass | Full pytest suite |
| CRAP | Pass | Maximum 7.0; threshold 30 |
| Full mutation | Pass | Score 0.920; 126 killed, 11 survived; threshold 0.8 |

No gates or mutation were rerun for this acceptance. The archived acceptance run and the re-audit report are the evidence.

## Implementation and verification

- LL-02 (#61), PR #75, landed the lend and return implementation.
- The first verification #78, PR #79, returned `changes-required` and identified application-policy coupling to Django.
- The re-verification #84, PR #85, returned `pass` after the use cases were moved behind application-owned Clock and LoanRepository ports.
- The independent audit LC-AUDIT #94, PR #95, found two misplaced ledger references.
- PR #98 corrected the stale ledger references.
- The re-audit LC-REAUDIT #100, PR #101, returned `complete`.

## Ledger status

| Ledger capability | Status | Verification | Tier |
|---|---|---|---|
| `loan.lend` | migrated | differential | A |
| `loan.return` | migrated | differential | A |
| `loan.return-date` | migrated | differential | A |

The re-audit confirmed that all three circulation ledger entries now name code that implements the capability.

## Human side-by-side check

Human check status: **requested**. This is a request only; the check has not been passed and nothing has been approved.

Compare the legacy Lending Library against the target implementation:

1. Lending through the API: required member and ISBN fields, blank-field 400 behavior, the 14-calendar-day due date using the server default time zone, and semicolon/delimiter escaping.
2. Returning through the API: first return succeeds, repeat return returns 409 with `already returned`, and the original return date remains unchanged.
3. Browser flows: `/ui/loans/new/` lending form and `/ui/loans/{id}/return/` return form, including validation and HTMX behavior.
