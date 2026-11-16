
## Handoff — afs-specialist-migrator · 2026-11-16T16:20:34Z
**State:** blocked  ·  **Branch / PR:** copilot/bk-05g-continue-dialogs-not-routed-table-yet-again  ·  **Last commit:** bc050afe
### Done
- See this branch's commits and `afs-run` journal.
### Remaining
- [ ] `.migration/returns/BK-05G.afs-specialist-migrator.yaml` has no `gates.mutation_changed`. Copy the score `afs-mutation` printed for your changed files from your journal; if it truly doesn't apply, write `n/a: <reason>` (e.g. `n/a: no mutable code changed`, or `n/a: not run, handed off`). It can't be left empty.
- [ ] Your return reports a handoff (`.migration/handoffs/BK-05G.md`) but this branch didn't commit it. Write the `## Handoff` section with afs-handoff and commit `.migration/handoffs/BK-05G.md`.
### Blockers / questions
- self-check failed: `afs-finish-check` still found 2 problem(s) after its retry budget (ADR-0034). Written by the stop hook, not by the agent.
### Next step for the next session
Fix the items under Remaining, run `afs-finish-check`, and commit. Scope items need the operator.
