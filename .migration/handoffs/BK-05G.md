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

## Handoff — afs-migrator · 2026-11-17T21:18:00Z
**State:** blocked  ·  **Branch / PR:** `copilot/fix-41807230-1458293352-d72ef3a3-ab9f-4210-8b1a-21636851476d` / https://github.com/martins-vds/ai-factory-eval/pull/1152  ·  **Last commit:** 5862a055
### Done
- Added accessible destination/deadline HTMX triggers and the shared native dialog shell in `templates/booking/dashboard/not_routed_table.html`.
- Build passed: `python -m compileall -q src` and `python manage.py check`, both exit 0 via `afs-run`.
- Behavior passed: `tests/booking/interfaces/test_dashboard.py`, 3 passed via `afs-run`.
- Regression passed: full suite, 461 passed via `afs-run`.
- Idiom passed: `ruff check` and `ruff format --check`, both exit 0 via `afs-run`.
- CRAP passed: `AFS-RESULT gate=crap max=26.0 threshold=30 over=0 methods=200`.
- Journal: `.migration/evidence/runs/BK-05G.md`.
### Remaining
- [ ] Resolve the missing dialog view/template and URL wiring before claiming that either dialog opens in this checkout.
- [ ] After the approved scope/dependency is available, add focused dialog interaction tests, run the changed-code mutation gate, and update the ledger and return.
### Decisions made
- Kept this change within the operator-approved template scope; did not add application views, dialog templates, URL configuration, tests, or ledger claims.
### Blockers / questions
- This checkout has no `src/cargotracker/booking/interfaces/dialogs/views.py`, `templates/booking/dialogs/`, `tests/booking/interfaces/test_dialogs.py`, or `src/cargotracker/booking/urls.py`; the global URL configuration does not register the destination/deadline paths.
- The new template requests `/admin/cargo/<tracking_id>/destination/` and `/deadline/`, but those paths have no handlers here. The current issue's AFS-SCOPE allows only the template, so the contract's stop rule blocks completing a working dialog flow without a scope/dependency decision.
- The existing dashboard tests and full suite do not exercise either dialog request; no E2E dialog evidence is claimed.
### Failing commands
- None. The changed-code mutation gate was not run because the required dialog flow is blocked and this return is a handoff.
### Next step for the next session
Ask the operator to authorize the missing BK-05G dialog views/templates and URL wiring in this checkout, or provide the prerequisite dialog implementation; then resume from this scope blocker, run setup again, and finish the dialog flow and its gates.
