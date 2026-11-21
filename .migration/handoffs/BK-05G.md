
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

## Handoff — afs-verifier · 2026-11-21T20:54:02Z
**State:** blocked  ·  **Branch / PR:** https://github.com/martins-vds/ai-factory-eval/pull/2172  ·  **Last commit:** dcfb78ef
### Done
- Build gates passed: `finish-build-compileall` and `finish-build-django-check`, exit 0.
- Ruff and layering checks passed; the UI check failed on three templates' unhandled htmx error responses.
- CRAP gate passed: `finish-crap-report`, exit 0, maximum 26.0.
- Changed-code mutation passed: `finish-mutation-changed`, exit 0, score 0.889.
- Migration validation passed before this handoff update.
### Remaining
- [ ] Have the BK-05G Migrator add htmx 4xx/5xx error handling to the table and both dialog forms.
- [ ] Re-run the UI gate through `afs-run`; update the verifier return and remove this handoff once the finding is resolved.
### Decisions made
- No production code was changed because this session is the Verifier; retain `verdict: changes-required` for the UI defect.
### Blockers / questions
- The verifier cannot fix the production-template defect under the role's test-only restriction.
### Failing commands
- `python .migration/harness/tools/check_ui.py` → exit 1, see `.migration/runs/BK-05G/20261121T204959167290Z-finish-idiom-ui.log:2-5`
### Next step for the next session
Dispatch a BK-05G Migrator to implement the UI error handling, then rerun the UI gate and resume verification. Scope items need the operator.
