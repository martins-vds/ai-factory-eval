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

## Handoff — afs-migrator · 2026-11-21T22:37:23Z
**State:** blocked  ·  **Branch / PR:** `copilot/fix-41807230-1458293352-911de3bb-f4bb-485e-afcf-e00473e54adf` / `martins-vds/ai-factory-eval#2233` (task issue; PR not provided)  ·  **Last commit:** d5ccd599
### Done
- Setup checks passed: pinned source SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`, migration validation passed, database healthy, Python 3.13.18, RTK 1.1.0.
- Setup probe passed; journal: `.migration/evidence/runs/BK-05G.md`.
- The expected base SHA `a383a407fb758d7640ff7600a4b9d2077cd53943` is present, but this checkout is at `65e3f9a2f5b490ccab718bd3ced7b546d35b0cb4` on a different branch.
- The expected base and current checkout both lack dialog view/template/test files; the not-routed template only has the route link, while the specification use cases are present.
### Remaining
- [ ] Restore the ticket's expected base/branch or provide the dialog handlers and templates as approved scope.
- [ ] Add dialog triggers to the not-routed table only after their endpoints are available; keep BK-05E tests green.
- [ ] Run the ticket gates and UI end-to-end verification through `afs-run`, then update the BK-05G return and ledger as authorized.
### Decisions made
- No application/template changes: the allowed template-only scope cannot create functional dialogs when their endpoints and templates are absent.
### Blockers / questions
- The issue states this checkout starts at `a383a407fb75` and names base branch `copilot/bk-05g-build-destination-deadline-dialogs`, but the actual checkout is at `65e3f9a2` on `copilot/fix-41807230-1458293352-911de3bb-f4bb-485e-afcf-e00473e54adf`.
- The operator scope permits only `templates/booking/dashboard/not_routed_table.html`; it does not permit adding the missing `src/cargotracker/booking/interfaces/dialogs/views.py` or `templates/booking/dialogs/` needed to handle the dialog requests.
### Failing commands
- None.
### Next step for the next session
Resume from the intended BK-05G dialog implementation base (or obtain approval to include the missing handler/template files), then implement the table integration within the approved scope.
