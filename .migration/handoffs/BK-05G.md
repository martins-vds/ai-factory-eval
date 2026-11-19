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

## Handoff — afs-migrator · 2026-11-19T18:43:30Z
**State:** blocked  ·  **Branch / PR:** `copilot/bk-05g-continue-dialogs-from-not-routed-table-46a4a76c-5e22-4d10-9b10-2632ebd715d5` / https://github.com/martins-vds/ai-factory-eval/pull/1588  ·  **Last commit:** 92ff499da445868d48c0355cf3bdc39b011fa069
### Done
- Implemented destination/deadline dialog views and templates, application-use-case updates, and not-routed table triggers.
- Final `behavior` and `regression` gates passed: 471 tests each; `.migration/evidence/runs/BK-05G.md`.
- Final build, Ruff, layer, UI, and CRAP gates passed; UI reported 0 findings and CRAP max was 26.0/30.
- Changed-code mutation passed at 0.837 (threshold 0.8); `.migration/evidence/mutants/BK-05G.md`.
- CodeQL reported zero alerts.
### Remaining
- [ ] Resolve production URL reachability for `/admin/cargo/<tracking_id>/destination/` and `/deadline/`.
- [ ] Once route wiring is in the approved checkout, rerun the HTTP flow and move the three dialog ledger entries from `in-progress` to `migrated`.
### Decisions made
- Did not edit `src/cargotracker/urls.py` or add `src/cargotracker/booking/urls.py`: BK-05G's approved scope excludes them; BK-05H owns URL registration.
### Blockers / questions
- This checkout's `src/cargotracker/urls.py` has no booking routes, so the table actions are not reachable through the production URL configuration.
- Local `.migration/plan/booking.tickets.yaml` still assigns registration to BK-05H (#295 in the live tracker), while live #295 is closed via PR #419. A human/coordinator must reconcile the local checkout with that completed work or explicitly extend BK-05G scope.
### Failing commands
- None remain. An initial mutation run scored 0.692; strengthened tests produced the passing 0.837 run.
### Next step for the next session
Ask the coordinator whether to port/restore BK-05H URL registration into this checkout or extend BK-05G scope; do not modify URL files until that scope is approved.
