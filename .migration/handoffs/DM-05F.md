## Handoff — afs-migrator · 2026-11-19T18:04:39Z
**State:** blocked  ·  **Branch / PR:** `copilot/dm-05f-load-data-invariants-again` (no PR identified)  ·  **Last commit:** 59ecd8ef
### Done
- Source checkout is present, read-only and pinned to `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`; target history is complete.
- Runtime and test services checks passed: Python 3.13.18 and `db` healthy.
- `afs-run --ticket DM-05F --name setup-probe -- true` passed; journal: `.migration/evidence/runs/DM-05F.md`, raw log: `.migration/runs/DM-05F/20261119T180456981578Z-setup-probe.log`.
- Ticket input check passes with the explicitly requested new test path excluded using `--ignore tests/data_migration/test_invariants.py`.
### Remaining
- [ ] Resolve the pre-existing migration validation errors in older ticket returns/evidence; this session did not modify those unrelated files.
- [ ] Restart `afs-setup-check`, then implement the requested invariant tests test-first and run the ticket gates.
### Decisions made
- No test or application files were changed; the named test file is intended to be created by this ticket.
### Blockers / questions
- Setup validation failed with 21 existing return/evidence inconsistencies, including mutation scores lacking matching journaled mutation gate runs. The failures affect tickets other than DM-05F and cannot be fixed within this ticket's scope.
### Failing commands
- `python .migration/harness/tools/validate.py .migration` → exit 1, reporting 21 errors in pre-existing return/evidence records.
### Next step for the next session
Resolve the pre-existing migration validation errors, rerun setup from the beginning, and only then continue DM-05F.
