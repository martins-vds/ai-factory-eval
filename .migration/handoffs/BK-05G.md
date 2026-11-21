
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

## Handoff — afs-verifier · 2026-11-21T19:20:04Z
**State:** needs human  ·  **Branch / PR:** copilot/bk-05g-verify-edit-dialogs-another-one / https://github.com/martins-vds/ai-factory-eval/pull/2094  ·  **Last commit:** 892fdd98
### Done
- Build, behavior, CRAP, mutation-changed and regression gates passed; see `.migration/evidence/runs/BK-05G.md`.
- Added missing-cargo 404 coverage for both dialog endpoints and strengthened invalid-input assertions.
- The idiom gate's `check_ui.py` step found missing htmx error handling in the table and both dialog forms.
### Remaining
- [ ] An authorized migrator must add htmx error-response handling to `templates/booking/dashboard/not_routed_table.html`, `templates/booking/dialogs/deadline.html`, and `templates/booking/dialogs/destination.html`.
- [ ] Re-run the idiom gate through `afs-run` and update verifier evidence and return after the fix.
### Decisions made
- No production templates were changed because the verifier role is read-only for production code.
- The return records `crap: 0` as the passed gate exit code; the CRAP maximum remains 26.0 in the gate journal.
### Blockers / questions
- The verifier found a major UI error-rendering defect requiring production changes outside verifier scope.
### Failing commands
- `bash -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` → exit 1, see `.migration/runs/BK-05G/20261121T191101352869Z-idiom.log:8-12`
### Next step for the next session
Have the authorized migrator fix the three template findings, rerun the idiom gate through `afs-run`, and resume BK-05G verification from the updated evidence.
