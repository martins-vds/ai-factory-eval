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

## Handoff — afs-migrator · 2026-11-19T18:04:21Z
**State:** blocked  ·  **Branch / PR:** `copilot/bk-05g-continue-dialogs-from-not-routed-table-d1e6441a-da0c-4daf-80aa-78e61e6d00b2` / https://github.com/martins-vds/ai-factory-pilot-target/pull/395  ·  **Last commit:** 3cf3d61134aced36ed5d122e717f76bef12bb853
### Done
- Source checkout is pinned to `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`, read-only and ignored; target HEAD ancestry is complete.
- Confirmed operator scope extension names `templates/booking/dashboard/not_routed_table.html`.
- No implementation, tests, or gates were run.
### Remaining
- [ ] Resolve the pre-existing migration-state validation errors preventing setup from passing.
- [ ] Restart all setup checks; only then resume the approved BK-05G implementation.
- [ ] Implement/test the dialog triggers in the scoped dashboard template, then run all ticket gates through `afs-run` and complete the return.
### Decisions made
- No files in the implementation scope were changed because setup validation failed and the migration contract requires stopping on a failed setup check.
### Blockers / questions
- `python .migration/harness/tools/validate.py .migration` reports 27 existing errors: multiple returns claim mutation scores without a matching mutation gate result in their evidence journals (AM-04B/C, BK-05A/B/C/D/E, DM-05A/C/D, FIX-109, HR-04B/C/D/E).
- These errors concern other tickets and must not be repaired as part of BK-05G. Setup must validate cleanly before this ticket continues.
### Failing commands
- `python .migration/harness/tools/validate.py .migration` → exit 1; setup output reported 27 unrelated mutation-evidence/return mismatches.
### Next step for the next session
Resolve the unrelated migration-state validation errors, then restart `afs-setup-check` from its first step before editing or running any BK-05G gates.
