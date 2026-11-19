## Handoff — afs-specialist-migrator · 2026-11-07T23:07:41Z
**State:** blocked  ·  **Branch / PR:** `copilot/bk-05g-build-destination-deadline-dialogs` / https://github.com/martins-vds/ai-factory-pilot-target/pull/395  ·  **Last commit:** ff8225e
### Done
- Setup checks passed; pinned source SHA is `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- Setup probe completed with exit 0; journal: `.migration/evidence/runs/BK-05G.md`.
- Confirmed the BK-05E dashboard template's not-routed table has no destination/deadline dialog triggers or dialog container.
### Remaining
- [ ] Resolve the ticket scope to allow updating `templates/booking/dashboard/not_routed_table.html` so the dialogs can be opened from the not-routed table.
- [ ] Implement and test BK-05G after scope is approved, then update the three dialog ledger entries and replace this handoff with passing gate evidence.
### Decisions made
- No application code was changed because the table integration requires a file outside the approved ticket scope.
### Blockers / questions
- BK-05G lists `src/cargotracker/booking/interfaces/dialogs/views.py`, `templates/booking/dialogs/`, and `tests/booking/interfaces/test_dialogs.py`, while the existing not-routed table is in `templates/booking/dashboard/not_routed_table.html`.
- The migration contract requires stopping and naming any additional required file; a human should approve adding the dashboard template to BK-05G or assign its UI integration to another ticket.
### Failing commands
- None.
### Next step for the next session
Resume BK-05G after the ticket scope explicitly includes `templates/booking/dashboard/not_routed_table.html`; then implement test-first and run the profile gates through `afs-run`.

## Handoff — afs-migrator · 2026-11-19T18:01:49Z
**State:** blocked  ·  **Branch / PR:** `copilot/bk-05g-continue-dialogs-not-routed-table-387d3b71-1d26-4ee0-a76c-152f7a496bf8` / https://github.com/martins-vds/ai-factory-pilot-target/pull/395  ·  **Last commit:** 36fb9bbc
### Done
- Source checkout is read-only and matches pinned SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`; target Git history is complete.
- Setup probe passed via `afs-run` (exit 0); journal: `.migration/evidence/runs/BK-05G.md`.
- Services and declared runtime checks passed: PostgreSQL service healthy; Python 3.13.18.
- No application code, tests, or ledger entries were changed.
### Remaining
- [ ] Resolve the migration-state validation failures listed below without weakening validation or fabricating gate evidence.
- [ ] Restart setup checks, then continue BK-05G within the approved template scope and run the ticket gates.
### Decisions made
- Stopped before implementation because setup check 3 found invalid pre-existing migration state; the stop rule prohibits continuing with gates or code changes.
### Blockers / questions
- `python .migration/harness/tools/validate.py .migration` reports 27 errors: prior returns for AM-04B/C, BK-05A/B/C/D/E, DM-05A/C/D, FIX-109, and HR-04B/C/D/04E-FIX/04E claim `mutation_changed` scores without a corresponding mutation gate result in their evidence journals. A migration-state owner must resolve these inconsistencies; they are outside BK-05G scope.
- The validation output was produced by the setup check and was not retained as an `afs-run` log. The setup-probe journal is not evidence that any ticket gate passed.
### Failing commands
- `python .migration/harness/tools/validate.py .migration` → exit 1; setup output reported 27 errors (no `afs-run` log; see blocker above).
### Next step for the next session
After the migration-state owner resolves the 27 validation errors, rerun the complete setup check from the beginning and resume BK-05G only if it passes.
