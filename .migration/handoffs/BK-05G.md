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

## Handoff — afs-migrator · 2026-11-22T17:16:43Z
**State:** blocked  ·  **Branch / PR:** `copilot/bk-05g-continue-dialogs-from-not-routed-table-6f2dc417-5eef-4128-a299-b1394c2a5d77` / no PR opened for this eval checkout  ·  **Last commit:** 8c135f55a
### Done
- Source is present, read-only and pinned at `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`; target history is complete.
- Migration validation passed; setup probe passed; database service is healthy; runtime check passed with Python 3.13.18.
- Confirmed `templates/booking/dashboard/not_routed_table.html` and `src/cargotracker/booking/application/specification.py` exist.
- No application code was changed.
### Remaining
- [ ] Resolve the setup-input mismatch for the three paths required by BK-05G, then rerun `afs-setup-check`.
- [ ] If setup passes, implement only the approved dashboard-template integration, run the ticket gates and update the return.
### Decisions made
- Stopped before implementation because `check_inputs.py` reports required BK-05G inputs missing; the operator scope extension does not make the listed dialog implementation inputs present.
### Blockers / questions
- `src/cargotracker/booking/interfaces/dialogs/views.py`, `templates/booking/dialogs/`, and `tests/booking/interfaces/test_dialogs.py` are absent from this checkout.
- The task scope extension restricts code changes to `templates/booking/dashboard/not_routed_table.html`; an operator must reconcile the missing ticket inputs with that extension. Do not fetch or merge the referenced base branch.
### Failing commands
- `python .migration/harness/tools/check_inputs.py` (journaled with `afs-run` as `setup-inputs-check`) → exit 1; see `.migration/runs/BK-05G/20261122T171655013676Z-setup-inputs-check.log`.
### Next step for the next session
Resolve the missing-input/setup mismatch with the operator; rerun setup from the beginning before touching application code.
