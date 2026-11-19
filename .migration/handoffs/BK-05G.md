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

## Handoff — afs-migrator · 2026-11-19T18:56:56Z
**State:** needs human  ·  **Branch / PR:** `copilot/bk-05g-continue-dialogs-not-routed-table-3edc17d2-f552-4504-b54d-3b2de32816f3` / https://github.com/martins-vds/ai-factory-eval/pull/1594  ·  **Last commit:** 16ec27c94379181ffd778a607dd41e62804d1086
### Done
- Destination and deadline dialogs are implemented and open from the not-routed table; all profile gates passed through `afs-run`.
- Browser E2E evidence is recorded at `.migration/evidence/ui/BK-05G.md`; isolated test database and temporary URL configuration were removed.
- Migration validation passed: 195 files checked, 0 errors.
### Remaining
- [ ] Decide whether `.migration/evidence/ui/BK-05G.md` may remain as required UI-specialty E2E evidence, or specify an approved existing evidence location.
- [ ] Apply that decision and rerun the harness finish check.
### Decisions made
- Keep the browser E2E report pending operator direction because `afs-specialty` requires an end-to-end run as UI evidence; silently deleting it would leave that run without durable evidence.
### Blockers / questions
- The operator-provided ADR-0034 finish check flags `.migration/evidence/ui/BK-05G.md` as outside BK-05G's planned files. The operator must decide whether to approve this evidence file or direct an in-scope alternative.
### Failing commands
- No profile gate failures. The finish-check finding was supplied by the operator; its command was not included.
### Next step for the next session
Resume after the operator decides how BK-05G's UI-specialty E2E evidence should be retained; apply that ruling, then rerun the finish check.
