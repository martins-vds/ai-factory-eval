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

## Handoff — afs-migrator · 2026-11-16T21:00:31Z
**State:** blocked  ·  **Branch / PR:** `copilot/bk-05g-continue-dialogs-routing` / https://github.com/martins-vds/ai-factory-eval/pull/732  ·  **Last commit:** `f6399bf5`
### Done
- Implemented destination/deadline dialog views and templates, application-use-case updates, and the not-routed table triggers. Focused UI/dashboard tests passed: 13/13; `.migration/evidence/runs/BK-05G.md`.
- Full regression passed: 471 tests. Build, idiom, and CRAP gates passed; CRAP max was 26.0. Changed-code mutation passed at 0.923 against 0.8. See `.migration/evidence/runs/BK-05G.md` and `.migration/evidence/mutants/BK-05G.md`.
- Updated the three BK-05G ledger entries.
### Remaining
- [ ] Resolve the current role/plan conflict so a schema-valid `.migration/returns/BK-05G.afs-migrator.yaml` can be committed.
- [ ] BK-05H must register the destination/deadline endpoints; that ticket owns `src/cargotracker/urls.py` and `src/cargotracker/booking/urls.py`.
### Decisions made
- Did not edit the plan or replace the prior specialist-migrator return because neither is in BK-05G's allowed file scope.
### Blockers / questions
- The current task requires role `afs-migrator` and return path `.migration/returns/BK-05G.afs-migrator.yaml`, but `.migration/plan/booking.tickets.yaml` still assigns BK-05G to retired role `afs-specialist-migrator`, and `.migration/returns/BK-05G.afs-specialist-migrator.yaml` already exists. `validate.py` rejects both role returns for one ticket ID. Operator approval is needed to update the plan/retire the prior return or otherwise resolve this conflict.
- Until BK-05H registers the routes, the new dashboard triggers target paths not yet registered in the application URL configuration.
### Failing commands
- `rtk python .migration/harness/tools/validate.py .migration` → exit 1: `.migration/plan/booking.tickets.yaml: ticket id BK-05G is already used by afs-migrator (.migration/returns/): pick a new id`.
### Next step for the next session
Ask the operator to resolve BK-05G's role/return conflict without widening this ticket's scope; then create the requested migrator return and run migration validation. Coordinate endpoint registration with BK-05H.
