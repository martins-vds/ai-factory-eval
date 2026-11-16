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

## Handoff — afs-specialist-migrator · 2026-11-16T13:58:49Z
**State:** blocked  ·  **Branch / PR:** copilot/bk-05g-continue-dialogs-from-table  ·  **Last commit:** de5dfa0d
### Done
- See this branch's commits and `afs-run` journal.
### Remaining
- [ ] `.migration/returns/BK-05G.afs-specialist-migrator.yaml` exists but this branch didn't update it. Update it with this session's gates and PR, and commit it.
- [ ] `.migration/returns/BK-05G.afs-specialist-migrator.yaml` has no `gates.mutation_changed`. Copy the score `afs-mutation` printed for your changed files from your journal; if it truly doesn't apply, write `n/a: <reason>` (e.g. `n/a: no mutable code changed`, or `n/a: not run, handed off`). It can't be left empty.
- [ ] Your return reports a handoff (`.migration/handoffs/BK-05G.md`) but this branch didn't commit it. Write the `## Handoff` section with afs-handoff and commit `.migration/handoffs/BK-05G.md`.
### Blockers / questions
- self-check failed: `afs-finish-check` still found 3 problem(s) after its retry budget (ADR-0034). Written by the stop hook, not by the agent.
### Next step for the next session
Fix the items under Remaining, run `afs-finish-check`, and commit. Scope items need the operator.
