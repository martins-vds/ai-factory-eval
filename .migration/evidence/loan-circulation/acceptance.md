# Loan circulation — acceptance

- Slice: `loan-circulation` (#60)
- Acceptance run: [42752283868, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868), successful on `main` at commit `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`
- Workflow: `.github/workflows/afs-acceptance.yml`; artifact: `afs-acceptance-70fef8e7bc822092770b04b1bf9b5288e04d8bb6-42752283868-1`, retained through 2026-12-10
- Archived result: `.migration/evidence/acceptance-runs/42752283868-1.json`
- Acceptance journal: `.migration/evidence/runs/LC-ACCEPT.md`

The archived result is for the requested repository, run attempt, and commit. GitHub Actions reports the graph, acceptance, and publish jobs successful. No acceptance gate or mutation was rerun for this acceptance.

## Gates

| Gate | Command | Exit | Notes |
|---|---|---:|---|
| Runtime, harness integrity, services, graph freshness | Acceptance workflow preflights | 0 | All passed |
| Source graph | `graph_gate.py --side source --require-graph` | 0 | 8 entry points; 6 reaching data |
| Target graph | `graph_gate.py --side target --require-graph --enforce-ownership` | 0 | 16 entry points; 12 reaching data |
| Build | `python -m compileall -q src`; `python manage.py check` | 0 | Both passed |
| Idiom | `ruff check src config manage.py tests`; `ruff format --check src config manage.py tests` | 0 | Both passed |
| Behavior | `pytest -q` | 0 | Acceptance suite passed |
| CRAP | `crap.py ... --max 30` | 0 | Maximum 7.0; threshold 30 |
| Full mutation | `python .migration/harness/tools/afs-mutation --all` | 0 | 0.920; threshold 0.8; 126 killed, 11 survived |

The detailed commands, exits, result values, and archived log hashes are in the acceptance rows of the run journal.

## Verification, audit, and characterization

LL-02 (#61) landed in PR #75. The first verification (#78, PR #79) required changes; the ports remediation was re-verified as passing in #84 / PR #85. The initial circulation audit (#94, PR #95) found misplaced ledger references for `loan.lend` and `loan.return-date`; PR #98 corrected them. The re-audit (#100, PR #101) reports `complete` with no capability gaps.

The three circulation capabilities have tier-A characterization. LL-02's tests cover required member and ISBN values, the 14-day due date, delimiter escaping, lending and return API behavior, repeat-return date preservation, and the lending/return browser flows.

## Ledger coverage

| Capability | Status | Evidence reviewed |
|---|---|---|
| `loan.lend` | `migrated` | Tier-A characterization; LL-02 API and browser tests cover required fields, due date, delimiter escaping, and loan creation |
| `loan.return` | `migrated` | Tier-A characterization; LL-02 tests cover successful return, missing loans, repeat-return `409`, and browser/HTMX return |
| `loan.return-date` | `migrated` | Tier-A characterization; LL-02 tests verify the saved first-return date remains unchanged on repeat return |

The re-audit confirms all three ledger target references resolve to the current implementation. The accepted target graph has one reported path inconsistency: it maps `POST /loans` through the listing/read path, while the inspected view branches to lending and behavior tests verify loan creation. The auditor classifies this as a graph-path inconsistency, not a capability gap. The 11 full-mutation survivors were reviewed against route and behavior tests in the final audit.

## Human side-by-side check — requested

Compare the legacy application against the target, side by side:

1. **API lending:** missing and blank member/ISBN fields, a successful loan's 14-day due date, and delimiter escaping in the resulting record.
2. **Returns:** the first return succeeds and saves its return date; a repeated return responds with HTTP `409` and leaves that saved date unchanged.
3. **Browser forms:** `/ui/loans/new/` and `/ui/loans/{id}/return/`, including successful submissions and validation/error behavior.

The human check remains requested. This report does not record human sign-off or approval.
