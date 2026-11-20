
## Handoff — afs-migrator · 2026-11-20T01:13:16Z
**State:** blocked  ·  **Branch / PR:** copilot/bk-05g-build-destination-deadline-dialogs-1852f95c-5612-428c-8a11-1474b1b06360  ·  **Last commit:** 41f26205
### Done
- See this branch's commits and `afs-run` journal.
### Remaining
- [ ] No return file. Write and commit `.migration/returns/BK-05G.afs-migrator.yaml` with `role: afs-migrator`, `ticket: BK-05G`, `issue:` this ticket's issue, `pr:` this PR, and every gate copied from your `afs-run` journal (`.migration/evidence/runs/BK-05G.md`). See afs-migration-contract → Return files.
### Blockers / questions
- self-check failed: `afs-finish-check` still found 1 problem(s) after its retry budget (ADR-0034). Written by the stop hook, not by the agent.
### Next step for the next session
Fix the items under Remaining, run `afs-finish-check`, and commit. Scope items need the operator.
