# Loan circulation — acceptance evidence

- Slice: `loan-circulation` · Acceptance run: [42752283868, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868) · Commit: `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`
- Archived result: `.migration/evidence/acceptance-runs/42752283868-1.json` · Artifact: `afs-acceptance-70fef8e7bc822092770b04b1bf9b5288e04d8bb6-42752283868-1` (retained through 2026-12-10).
- The archived run reports `status: passed`, exit 0, and all 15 steps passed. No acceptance gate or mutation was rerun for this acceptance.

## Gates

| Gate | Exit | Result |
|---|---:|---|
| Runtime, harness integrity, services, graph freshness | 0 | All preflight steps passed. |
| Source graph | 0 | Pass; 8 entry points, 6 reaching data. |
| Target graph | 0 | Pass; 16 entry points, 12 reaching data. |
| Build | 0 | `compileall` and `manage.py check` passed. |
| Idiom | 0 | `ruff check` and `ruff format --check` passed. |
| Behavior | 0 | `pytest -q` passed. |
| CRAP | 0 | Maximum 7.0 against threshold 30. |
| Full mutation | 0 | Score 0.920 against threshold 0.8; 126 killed, 11 survived. |

The acceptance-run journal records the archived commands, results, and log hashes at `.migration/evidence/runs/LC-ACCEPT.md`. The 11 survivors were six route literals, four method guards, and `LoanForm.Meta.model`; the audit reviewed the relevant API and browser behavior tests, including unsupported-method responses, rather than treating the aggregate score as coverage proof.

## Implementation and audit trail

LL-02 (#61) landed in PR #75. Its first verification (#78, PR #79) required changes; the ports remediation was re-verified as passing by #84 (PR #85). LC-AUDIT (#94, PR #95) identified two misplaced ledger references. PR #98 corrected them, and LC-REAUDIT (#100, PR #101) returned `complete` with no capability gaps.

The re-audit confirms all three ledger entries are `migrated`, and their target components resolve:

| Capability | Target components | Evidence and status |
|---|---|---|
| `loan.lend` | `LoanForm`, `LoanApplication.lend`, `loan_collection`, `loan_lend_page` | Endpoint tests cover required/blank fields, 201 creation, the 14-day due date, and delimiter escaping; browser/HTMX lending tests pass. Ledger status: `migrated`. |
| `loan.return-date` | `DjangoLoanRepository.mark_returned`, `LoanApplication.return_loan` | Tests cover the first persisted return date and preservation of that date on repeat; service tests exercise the application ports. Ledger status: `migrated`. |
| `loan.return` | `loan_return`, `loan_return_page`, `loans.urls` | Tests cover successful return, 404/409 responses, and browser/HTMX return behavior. Ledger status: `migrated`. |

The tier-A characterization, LL-02 test-first journal, and final verifier support these behaviors. Approved rulings #39, #41, and #43 account for blank-field rejection, repeated-return rejection/date preservation, and delimiter escaping.

The audit also reported a target-graph under-description: its `POST /loans` path points to `LoanApplication.list_loans_text`/a read, while the inspected view branches POST to `loan_lend` and behavior tests verify creation. The Auditor judged this a graph inconsistency, not a missing capability; it remains visible for follow-up.

## Ticket reconciliation

`.migration/evidence/ticket-reconciliation/60.yaml` records completed dispositions for #61, #78, #84, #94, #100, and coordinator ticket #108. The read-only `reconcile_epic.py --dry-run` attempt could not query GitHub (`gh api` returned HTTP 403); dispositions were populated from the live issue and linked-PR records available through read-only GitHub issue reads. PR #109 is the open acceptance PR and is cited for #108; CI should check it as-if-merged.

## Human side-by-side check

**Requested, not performed.** Compare legacy observations with the target, checking the approved divergences explicitly:

1. Lending through the API: missing/blank required member and ISBN fields, valid creation and the 14-day due date, and delimiter-containing values in exported fields (approved outcomes: reject blank fields and escape delimiters).
2. Returning through the API: the first successful return, then a repeat that returns HTTP 409 and leaves the saved return date unchanged (approved ruling #41).
3. Target `/ui/loans/new/` and the return form: required-field validation, successful lending/return, and repeat-return error behavior against the corresponding legacy API outcomes.

No human sign-off or approval is recorded here. The slice epic remains open until the operator's side-by-side check and approver review are complete.
