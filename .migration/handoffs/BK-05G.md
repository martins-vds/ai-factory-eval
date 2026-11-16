
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

## Handoff — afs-verifier · 2026-11-16T18:17Z
**State:** blocked  ·  **Branch / PR:** copilot/eval-2026-11-16-b3c-r3-verify-bk-05g / martins-vds/ai-factory-eval#690  ·  **Last commit:** e1711083
### Done
- Setup passed; source SHA matched `.migration/source.lock`: `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- Build, behavior, idiom, CRAP and regression passed; see `.migration/evidence/runs/BK-05G.md`.
- Added both destination and deadline unknown-ID 404 cases; focused tests and both full-suite runs passed.
- Reviewed the table change against PR #402's base/head and confirmed the existing dashboard tests and dashboard view are unchanged.
### Remaining
- [ ] Re-run the changed-code mutation gate to completion; the interrupted run has no score and no successful journal row.
- [ ] Inspect the completed mutation survivor diffs for BK-05G behavior and update this return with the exact score.
- [ ] Reconcile the stale `booking.screen-not-routed-table` ledger status/notes through its owner; verifier did not edit the ledger.
### Decisions made
- Kept the shared table ledger unchanged because verifier scope is limited to tests, journal and return.
### Blockers / questions
- Operator requested time-constrained completion while `afs-mutation --changed-since origin/main` was still running. Its run began at `.migration/runs/BK-05G/20261116T173915164685Z-verifier-mutation-changed.log`; it was stopped before an `AFS-RESULT`.
- The eval checkout's `origin/main` differs from the target PR base; `git diff origin/main...HEAD -- src` lists 128 files, and target base `515e85f56e3e81024eafce9679343b7c0c126a7f` is not present locally. Confirm the intended mutation scope before counting its result.
### Failing commands
- None completed with a failure; the mutation command was interrupted before completion.
### Next step for the next session
Resume BK-05G verification, complete the configured mutation gate on the appropriate target baseline, inspect its survivors, then update and validate the verifier return.
