
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

## Handoff — afs-verifier · 2026-11-21T13:28:08Z
**State:** blocked  ·  **Branch / PR:** https://github.com/martins-vds/ai-factory-eval/pull/2020  ·  **Last commit:** 6e74f10
### Done
- Added focused unknown/stale-ID and route-state reset tests; build, behavior, CRAP, changed-code mutation, and regression gates passed.
- `idiom-ui-errors` failed with exit 1 because htmx 4xx/5xx responses are not rendered in the dialog (`.migration/evidence/runs/BK-05G.md`).
### Remaining
- [ ] Resolve the dialog htmx error-rendering findings in the production templates and rerun the idiom gate through `afs-run`.
- [ ] Re-verify the ticket after the implementation fix.
### Decisions made
- The verifier does not change production code; the implementation defect remains a major finding.
### Blockers / questions
- The failed idiom gate concerns production template behavior, outside the verifier's allowed changes.
### Failing commands
- `python .migration/harness/tools/check_ui.py` → exit 1, see `.migration/evidence/runs/BK-05G.md` (`idiom-ui-errors`).
### Next step for the next session
Have a Migrator fix the htmx error-rendering behavior, rerun the idiom gate through `afs-run`, and then resume BK-05G verification.
