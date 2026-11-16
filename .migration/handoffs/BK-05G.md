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

## Handoff — afs-migrator · 2026-11-16T20:55:40Z
**State:** blocked  ·  **Branch / PR:** `copilot/bk-05g-continue-dialogs-from-table-another-one` / https://github.com/martins-vds/ai-factory-pilot-target/pull/395  ·  **Last commit:** f4365992
### Done
- Setup checks passed for pinned source SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`; migration validation, input check, service check, runtime check, and setup probe all exited 0.
- Reviewed the authorized dashboard template and the booking URL configuration. The current checkout contains no dialog views, dialog templates, dialog URL registration, or tests; searches for `create_destination_dialog_view`, `create_deadline_dialog_view`, `destination-dialog`, and `deadline-dialog` found no matches.
- No application/template change was made because adding openers to the authorized template alone would send requests to endpoints that do not exist in this checkout.
### Remaining
- [ ] Align the checkout with the BK-05G implementation base containing the dialog endpoints/templates, or have the operator explicitly extend scope to include the missing views, templates, URL registration, and tests.
- [ ] Implement the integration test-first, change only authorized files, and run all applicable profile gates through `afs-run`.
- [ ] Update the return and ledger as appropriate after the scope blocker is resolved.
### Decisions made
- Do not add nonfunctional HTMX openers to `templates/booking/dashboard/not_routed_table.html`; preserve BK-05E behavior until the dialog endpoints are available.
### Blockers / questions
- The operator scope extension authorizes only `templates/booking/dashboard/not_routed_table.html`, while the current checkout lacks the backend and template endpoints needed to make its dialog openers work. The out-of-scope rule requires stopping until the correct implementation base is checked out or scope is expanded.
- The requested `.migration/returns/BK-05G.afs-migrator.yaml` is rejected as a duplicate: `.migration/returns/BK-05G.afs-specialist-migrator.yaml` already occupies the normalized Migrator return for BK-05G. Keep the existing valid return unless the operator resolves supersession/path handling.
### Failing commands
- None. The dialog-symbol search returned no matches (exit 1), confirming the blocker.
### Next step for the next session
Resume only after the operator aligns the checkout with the BK-05G dialog implementation or approves scope for the missing dialog views/templates/routes/tests, and resolves how the return file should be superseded without creating a duplicate; then wire the table controls and run the required gates.
