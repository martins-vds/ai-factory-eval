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

## Handoff — afs-specialist-migrator · 2026-11-15T05:59:17Z
**State:** blocked  ·  **Branch / PR:** `copilot/bk-05g-continue-dialogs` / https://github.com/martins-vds/ai-factory-eval/pull/123  ·  **Last commit:** c45b143
### Done
- Setup checks passed; pinned source SHA is `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- Focused dialog/dashboard tests, full behavior tests, build checks, Ruff check/format, and CRAP gate passed; see `.migration/evidence/runs/BK-05G.md` (CRAP max 26.0, threshold 30).
- Updated the three BK-05G dialog ledger entries and this return file.
### Remaining
- [ ] Resolve scope for `src/cargotracker/booking/interfaces/dialogs/__init__.py` and `templates/booking/dashboard/not_routed_table.html`, which are outside BK-05G's planned file list.
- [ ] After scope is resolved, run the changed-code mutation gate and update this return.
### Decisions made
- Retained the package marker for the new dialogs package and the dashboard template because the package marker follows the project's package layout and the template contains the controls needed to open the dialogs.
### Blockers / questions
- The ticket's planned files omit both paths above. An operator must add them to BK-05G's scope or assign their work to another ticket before proceeding.
### Failing commands
- Initial dialog test collection/focused runs and the first Ruff format check failed; corrected reruns passed, as recorded in `.migration/evidence/runs/BK-05G.md`. No failing gate remains other than the not-yet-run mutation gate.
### Next step for the next session
Ask the operator to resolve the two out-of-scope paths, then run `afs-mutation` for BK-05G's changed code and refresh the return.
