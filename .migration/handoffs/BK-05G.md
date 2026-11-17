
## Handoff — afs-specialist-migrator · 2026-11-08T00:38:10Z
**State:** blocked  ·  **Branch / PR:** copilot/bk-05g-continue-dialogs-not-routed-table  ·  **Last commit:** 188581d
### Done
- See this branch's commits and `afs-run` journal.
### Remaining
- [ ] These files are outside ticket BK-05G's planned files: `.migration/handoffs/BK-05G.bk05e-dashboard-template.md`. Don't widen your own scope: revert them, or, if the work truly needs them, write a handoff (afs-handoff) that names each file and why, set `handoff:` in your return, and stop. The operator decides.
### Blockers / questions
- self-check failed: `afs-finish-check` still found 1 problem(s) after its retry budget (ADR-0034). Written by the stop hook, not by the agent.
### Next step for the next session
Fix the items under Remaining, run `afs-finish-check`, and commit. Scope items need the operator.

## Handoff — afs-verifier · 2026-11-17T13:26:45Z
**State:** blocked  ·  **Branch / PR:** copilot/martins-vdsai-factory-pilot-target294-verify-bk-05-another-one  ·  **Last commit:** cb6e017d
### Done
- See this branch's commits and `afs-run` journal.
### Remaining
- [ ] No return file. Write and commit `.migration/returns/BK-05G.afs-verifier.yaml` with `role: afs-verifier`, `ticket: BK-05G`, `issue:` this ticket's issue, `pr:` this PR, and every gate copied from your `afs-run` journal (`.migration/evidence/runs/BK-05G.md`). See afs-migration-contract → Return files.
### Blockers / questions
- self-check failed: `afs-finish-check` still found 1 problem(s) after its retry budget (ADR-0034). Written by the stop hook, not by the agent.
### Next step for the next session
Fix the items under Remaining, run `afs-finish-check`, and commit. Scope items need the operator.
