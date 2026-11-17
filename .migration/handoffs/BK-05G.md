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

## Handoff — afs-migrator · 2026-11-17T21:47:55Z
**State:** blocked  ·  **Branch / PR:** `copilot/fix-41807230-1458293352-85eca0fc-489a-4841-82b2-55dca4a0bae6` / n/a  ·  **Last commit:** 471cc464
### Done
- Updated only `templates/booking/dashboard/not_routed_table.html` with destination/deadline dialog triggers and a shared accessible dialog shell; preserved the route link, table data, and existing displayed values.
- Build gates passed: `compileall` and `manage.py check` exit 0; `.migration/runs/BK-05G/20261117T214459430015Z-build-compile.log`, `.migration/runs/BK-05G/20261117T214459523973Z-build-check.log`.
- Dashboard behavior passed: 3 tests, exit 0; `.migration/runs/BK-05G/20261117T214409370825Z-behavior-dashboard.log`.
- Idiom gates passed: `ruff check` and `ruff format --check` exit 0; `.migration/runs/BK-05G/20261117T214502265310Z-idiom-lint.log`, `.migration/runs/BK-05G/20261117T214502322182Z-idiom-format.log`.
- CRAP gate passed at 26.0 (maximum 30); `.migration/runs/BK-05G/20261117T214634950415Z-crap-score.log`.
- Changed-code mutation reported `n/a: no mutable code changed`; `.migration/runs/BK-05G/20261117T214657113776Z-mutation-changed.log`.
- Full regression passed: 461 tests, exit 0; `.migration/runs/BK-05G/20261117T214505022821Z-regression.log`.
### Remaining
- [ ] Run dialog end-to-end coverage against the complete BK-05G implementation and record its evidence.
- [ ] Update the return with the resulting PR link and any ledger evidence permitted by the ticket scope.
### Decisions made
- Kept the application edit to the operator-authorized dashboard template. Did not add views, dialog templates, routes, or tests outside that scope.
### Blockers / questions
- This checkout has no `src/cargotracker/booking/interfaces/dialogs/views.py`, `templates/booking/dialogs/`, or dialog route definitions. Therefore the new triggers cannot be exercised end-to-end here. The operator scope extension authorizes only the not-routed template, so do not add those missing files without a corrected checkout or scope decision.
### Failing commands
- None.
### Next step for the next session
Resume on a checkout containing the already-approved BK-05G dialog views/templates/routes, or obtain approval to add the missing files; then run the dialog end-to-end tests, update the return's evidence, and resolve this handoff.
