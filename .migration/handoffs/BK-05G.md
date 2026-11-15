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

## Handoff — afs-specialist-migrator · 2026-11-15T17:48:59Z
**State:** blocked  ·  **Branch / PR:** `copilot/fix-41807230-1458293352-e1c8b608-b1d9-4db7-ab72-275f9523c53e` / martins-vds/ai-factory-eval#298  ·  **Last commit:** dded5823
### Done
- Setup passed with pinned source SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`; migration validation passed (194 files, 0 errors).
- Setup probe passed; log: `.migration/runs/BK-05G/20261115T174741836417Z-setup-probe.log`.
- Confirmed `specification.py` exposes destination and deadline update use cases, but no booking dialog views, dialog templates, or booking URL routes exist in this checkout. The root URL configuration does not include booking routes.
- The operator scope extension permits changes only to `templates/booking/dashboard/not_routed_table.html`. ADR-0001 requires interface views to call application use cases, so template-only triggers cannot open functional dialogs here.
### Remaining
- [ ] Human/operator: provide the missing dialog implementation and routes in this checkout, or extend the permitted file scope to add them and their tests.
- [ ] After that decision, add the table triggers, run the focused dashboard/dialog tests and all required gates through `afs-run`, and update the return.
### Decisions made
- Left `templates/booking/dashboard/not_routed_table.html` unchanged rather than add links to nonexistent endpoints.
### Blockers / questions
- The approved template-only scope is insufficient to provide working dialogs because the dialog views, templates and routes are absent. The handoff stop rule applies; do not make out-of-scope application changes without operator approval.
### Failing commands
- None.
### Next step for the next session
Ask the operator to resolve the scope/prerequisite gap, then implement the confirmed dialog integration and verify the BK-05E dashboard behavior.
