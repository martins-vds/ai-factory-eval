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

## Handoff — afs-specialist-migrator · 2026-11-16T03:59:00Z
**State:** blocked  ·  **Branch / PR:** `copilot/fix-41807230-1458293352-5663ae04-d841-4425-b4c9-98dbd6b5a8a0` / https://github.com/martins-vds/ai-factory-eval/issues/518  ·  **Last commit:** 43b976a4
### Done
- Source pin/read-only check passed: `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`; target history is complete; migration validation passed; Python runtime and DB service checks passed.
- Setup probe passed via `afs-run`: `.migration/runs/BK-05G/20261116T035813873640Z-setup-probe.log`.
- Confirmed the operator's scope extension names `templates/booking/dashboard/not_routed_table.html`.
### Remaining
- [ ] Restore or provide the correct BK-05G target checkout and verify all ticket inputs before implementing.
- [ ] Implement the dialog trigger integration, then run the requested gates through `afs-run` and update the return.
### Decisions made
- No application code was changed because the required dialog view, dialog templates, and dialog tests named by BK-05G are absent from this checkout.
### Blockers / questions
- The required `check_inputs.py` setup check failed: `src/cargotracker/booking/interfaces/dialogs/views.py`, `templates/booking/dialogs/`, and `tests/booking/interfaces/test_dialogs.py` are missing. The migration contract requires stopping when named inputs are missing; the dashboard template scope extension alone does not provide the dialog implementation or test inputs.
- This checkout is `martins-vds/ai-factory-eval`, while the BK-05G ticket and base PR belong to `martins-vds/ai-factory-pilot-target`. Confirm the correct target checkout is available before resuming.
### Failing commands
- `python .migration/harness/tools/check_inputs.py` with BK-05G input paths → exit 1; reported 3 missing paths.
### Next step for the next session
Run the session in the correct `ai-factory-pilot-target` checkout (or make the named BK-05G inputs available), rerun setup from the beginning, then implement only the approved dashboard-template integration and proceed with the ticket.
