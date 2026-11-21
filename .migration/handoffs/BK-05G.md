
## Handoff — afs-migrator · 2026-11-21T13:45:24Z
**State:** blocked  ·  **Branch / PR:** copilot/bk-05g-build-destination-deadline-dialogs-49042d50-8e83-4898-8b67-1fb269a36395  ·  **Last commit:** fa44af82
### Done
- See this branch's commits and `afs-run` journal.
### Remaining
- [ ] You changed `src/cargotracker/booking/interfaces/dialogs/views.py` after your last run of `build`, `behavior`, `idiom`, `crap`, so those results don't describe the code CI will check. Re-run each through afs-run and copy the new results into your return.
### Blockers / questions
- self-check failed: `afs-finish-check` still found 1 problem(s) after its retry budget (ADR-0034). Written by the stop hook, not by the agent.
### Next step for the next session
Fix the items under Remaining, run `afs-finish-check`, and commit. Scope items need the operator.
