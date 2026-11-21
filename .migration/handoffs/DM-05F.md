## Handoff — afs-migrator · 2026-11-21T22:39:00Z
**State:** blocked  ·  **Branch / PR:** copilot/fix-41807230-1458293352-74114f3d-da0c-460e-8aed-07ad3ae76d6e  ·  **Last commit:** e5dfd58
### Done
- Source checkout is read-only and matches `.migration/source.lock` at `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`; target ancestry is complete.
- Migration validation passed: `python .migration/harness/tools/validate.py .migration` (183 files, 0 errors).
- Services and runtime checks passed; `afs-run` setup probe passed (exit 0), recorded in `.migration/evidence/runs/DM-05F.md`.
- Confirmed `tests/data_migration/test_invariants.py` is a ticket-created path and excluded it from input validation; `.migration/data/snapshot/` remains missing.
### Remaining
- [ ] Have setup steps or the snapshot owner place the required snapshot in `.migration/data/snapshot/`.
- [ ] Rerun setup input validation, then implement the requested loaded-data invariant tests and complete ticket gates.
### Decisions made
- Did not create tests or use a substitute fixture while the required snapshot input is unavailable.
### Blockers / questions
- Setup rule: a missing named input is a stop, not an invitation to fabricate or bypass it. The snapshot is required to exercise `load_data_snapshot` against loaded data.
- The setup check command `python .migration/harness/tools/check_inputs.py --ignore tests/data_migration/test_invariants.py` exited 1 because `.migration/data/snapshot/` is missing; this setup command does not produce an `afs-run` log.
### Failing commands
- `python .migration/harness/tools/check_inputs.py --ignore tests/data_migration/test_invariants.py` → exit 1; setup output reports the missing `.migration/data/snapshot/` input.
### Next step for the next session
Fetch the pinned snapshot into `.migration/data/snapshot/` using the approved setup procedure, rerun `afs-setup-check`, then resume DM-05F by adding the invariant tests in the ticket-listed test file.
