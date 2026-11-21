# Loan circulation — acceptance evidence

- Tickets: LL-02 (#61), verifier #78 / #84, audits #94 / #100, and acceptance #108
- Acceptance run: [42752283868, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868), on commit `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`
- Archived result: `.migration/evidence/acceptance-runs/42752283868-1.json` (artifact retention through 2026-12-10)
- Date: 2026-11-21

No acceptance gates or mutation were rerun for this ticket. The archived result and the audit evidence record:

## Gates

| Gate | Command | Exit | Result |
|---|---|---:|---|
| Preflight | Runtime, harness integrity, services, graph freshness | 0 | All preflight steps passed |
| Source graph | `graph_gate.py --side source --require-graph` | 0 | Pass; 8 entry points, 6 reaching data |
| Target graph | `graph_gate.py --side target --require-graph --enforce-ownership` | 0 | Pass; 16 entry points, 12 reaching data |
| Build | `python -m compileall -q src`; `python manage.py check` | 0 | Both steps passed |
| Idiom | `ruff check src config manage.py tests`; `ruff format --check src config manage.py tests` | 0 | Both steps passed |
| Behavior | `pytest -q` | 0 | Full acceptance suite passed |
| CRAP | Coverage, Lizard, and `crap.py` | 0 | Maximum 7.0; threshold 30 |
| Full mutation | `python .migration/harness/tools/afs-mutation --all` | 0 | Score 0.920; 126 killed, 11 survived; threshold 0.8 |

The archive's complete results and the unchanged run rows are in `.migration/evidence/runs/LC-ACCEPT.md`.

## Characterization and verification history

The circulation capabilities are tier-A characterized. LL-02's journal records failing-then-passing lending and return tests. The initial verification (#78, PR #79) found Django/concrete repository coupling; the follow-up verification (#84, PR #85) records the port remediation and a pass.

The initial audit (#94, PR #95) found misplaced target references for `loan.lend` and `loan.return-date`. PR #98 corrected the references, and the re-audit (#100, PR #101) returned `complete` with no capability gaps.

## Capability coverage

| Ledger entry | Status | Evidence summary |
|---|---|---|
| `loan.lend` | `migrated` | Tier-A evidence and LL-02 tests cover required/blank fields, the 14-day due date, delimiter escaping, API lending, and the new-loan UI. |
| `loan.return` | `migrated` | Tier-A evidence and LL-02 tests cover successful API and browser returns, unknown loans, and repeat-return `409` behavior. |
| `loan.return-date` | `migrated` | Tier-A evidence and LL-02 tests verify the first return date persists and a repeated return leaves it unchanged. |

The re-audit confirms all three ledger entries reference existing implementation components. The accepted target graph has one reported path inconsistency: it maps `POST /loans` through a read/list path, while the inspected view branches to lending and behavior tests verify loan creation. The Auditor records this as a graph-path inconsistency, not a capability gap. The 11 mutation survivors were reviewed against route, method-guard, and form-model behavior tests.

## Human check — requested

Compare legacy behavior against the target side by side:

1. **API lending:** Send equivalent `POST /loans` requests. Compare required member and ISBN validation, the 14-day due date, and delimiter escaping in the resulting record and response.
2. **API returns:** Compare the first `POST /loans/{id}/return` result and saved return date, then repeat the request. Confirm the target returns `409` and preserves the original saved date as the legacy behavior requires.
3. **Target forms:** Exercise `/ui/loans/new/` and `/ui/loans/{id}/return/`; compare their successful outcomes and validation/error behavior with the corresponding legacy API behaviors.

The human check remains requested. No sign-off or approval is recorded.
