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

## Handoff — afs-migrator · 2026-11-21T19:02:04Z
**State:** blocked  ·  **Branch / PR:** `copilot/bk-05g-continue-dialogs-not-routed-table-b2f763d6-ed3c-4c60-863f-d84da7879988` / PR link unavailable in this session  ·  **Last commit:** `15370518`
### Done
- Setup checks passed; pinned source SHA is `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- The corrected `check_inputs.py` check found both authorized inputs and reported 0 missing paths.
- The `setup-probe` run passed (exit 0); journal: `.migration/evidence/runs/BK-05G.md`.
- Confirmed `CargoSpecification.change_destination` and `.change_deadline` exist, but no dialog view, dialog template, or dialog endpoint exists in the checkout. The authorized not-routed template currently renders display-only destination and deadline cells.
### Remaining
- [ ] Obtain an operator decision: authorize the missing dialog view/template/route implementation outside the template-only scope, or identify already-implemented dialog endpoints and templates.
- [ ] Once supporting dialogs exist and scope is explicit, wire the not-routed table to them without changing BK-05E table behavior; then run the applicable tests and all ticket gates through `afs-run`.
### Decisions made
- No application template or code was changed. Editing only the not-routed table cannot open functional dialogs when the dialog endpoints and templates are absent; adding them would exceed the operator-authorized scope.
### Blockers / questions
- The operator scope permits only `templates/booking/dashboard/not_routed_table.html`, but the required dialog view, templates, and route are not present. A template-only change would introduce links or htmx requests that cannot resolve to dialogs.
- The application integration must call the existing `CargoSpecification` use cases through a view; it must not call them directly from a template.
### Failing commands
- None.
### Next step for the next session
Ask the operator to authorize the missing dialog support paths or provide their existing implementation, then resume the template-only integration within the approved scope.
