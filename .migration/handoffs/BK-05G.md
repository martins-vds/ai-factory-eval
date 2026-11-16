## Handoff — afs-migrator · 2026-11-16T21:04:06Z
**State:** needs human · **Branch / PR:** `copilot/bk-05g-continue-dialogs-from-table-again` / https://github.com/martins-vds/ai-factory-eval/pull/742 · **Last commit:** 593b022c295445897c227bdd3ca6da795c9a6293

### Done
- BK-05G dialogs and dashboard launch actions are implemented. Build, behavior, idiom, CRAP (26.0), changed-code mutation (0.970), and full regression (470 passed) gates passed; see `.migration/evidence/runs/BK-05G.md`.
- The operator-approved scope extension names `templates/booking/dashboard/not_routed_table.html`; the finish check still flags the associated ledger entry and plan role change as outside the ticket's planned files. Finding is recorded in `.migration/evidence/finish-check/9984e74b-6995-400b-8dde-cb1d467fdbb4.json`.

### Remaining
- [ ] Operator decides whether `.migration/ledger/booking.screen-not-routed-table.yaml` may be updated to record the newly added dialog actions and dashboard refresh.
- [ ] Operator decides whether `.migration/plan/booking.tickets.yaml` may change BK-05G's role from `afs-specialist-migrator` to `afs-migrator`, matching the active task role and return contract.

### Decisions made
- Kept both files pending operator direction: reverting the ledger would leave the table capability's new behavior unrecorded; reverting the plan would conflict with the active task's `afs-migrator` role. No additional application-code changes were made.

### Blockers / questions
- ADR-0034 finish check blocked completion on these two out-of-scope paths. Operator must approve both changes or direct their reversion.

### Failing commands
- No gate command is failing. The finish-check scope decision is a block, recorded in `.migration/evidence/finish-check/9984e74b-6995-400b-8dde-cb1d467fdbb4.json`.

### Next step for the next session
Follow the operator's decision for the two named paths, update this return's ledger and handoff fields accordingly, then rerun migration validation and the finish check.
