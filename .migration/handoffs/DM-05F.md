
## Handoff — afs-migrator · 2026-11-23T01:46:34Z
**State:** blocked  ·  **Branch / PR:** copilot/dm-05f-business-invariants-check-one-more-time  ·  **Last commit:** f22d7568c
### Done
- See this branch's commits and `afs-run` journal.
### Remaining
- [ ] You changed `tests/data_migration/test_invariants.py` after your last run of `build`, so those results don't describe the code CI will check. Re-run each through afs-run and copy the new results into your return.
### Blockers / questions
- self-check failed: `afs-finish-check` still found 1 problem(s) after its retry budget (ADR-0034). Written by the stop hook, not by the agent.
### Next step for the next session
Fix the items under Remaining, run `afs-finish-check`, and commit. Scope items need the operator.
