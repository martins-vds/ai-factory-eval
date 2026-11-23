## Handoff — afs-migrator · 2026-11-23T00:58:03Z
**State:** needs human  ·  **Branch / PR:** https://github.com/martins-vds/ai-factory-eval/pull/2426  ·  **Last commit:** e2b97254a
### Done
- Implemented the mapping-driven `export_data_snapshot` command and CSV exporter; fixture round-trip, NULL/empty-string, UTC timestamp and primary-key-order tests pass.
- Snapshot validation passed: 7 tables, 0 problems; `.migration/runs/DM-05D/20261123T004407158536Z-snapshot-check.log`.
- Live export reconciled all 54 mapped rows across 6 tables with matching checksums and no problems; `.migration/runs/DM-05D/20261123T004748978235Z-snapshot-reconcile.log`.
- Final full suite passed (424 tests), CRAP max 26.0 / threshold 30, and changed-code mutation scored 0.855 / threshold 0.8; see `.migration/evidence/runs/DM-05D.md`.
- CodeQL found no alerts. `.migration/returns/DM-05D.afs-migrator.yaml` records the gate results.
### Remaining
- [ ] Human decision: authorize `.migration/evidence/flaky/DM-05D.md` as a scope extension, or direct how to resolve the conflict without discarding the AFS-FLAKY record.
- [ ] After scope authorization, rerun `python -m compileall -q src` and `python manage.py check` through `afs-run` (the finish check requires fresh build evidence after the final test-file edit), then clear this handoff only if the finish check accepts the scope.
### Decisions made
- Kept the generated flaky-run record: the first snapshot load failed because the target database migrations were not applied; after `python manage.py migrate --noinput`, the load passed. The failure and recovery are preserved in `.migration/evidence/flaky/DM-05D.md`.
### Blockers / questions
- The finish check rejected `.migration/evidence/flaky/DM-05D.md` because it is outside DM-05D's planned files. The ticket also says to touch only its listed files, while the AFS-FLAKY harness says to record and commit this generated file. Operator authorization is required.
### Failing commands
- `python manage.py load_data_snapshot --snapshot .migration/data/snapshot/ --mapping .migration/data/mapping.yaml` → exit 1 before applying target migrations; `.migration/runs/DM-05D/20261123T004730564619Z-snapshot-load.log:61-65`.
### Next step for the next session
Ask the operator to resolve the scope conflict for `.migration/evidence/flaky/DM-05D.md`. If authorized, rerun the two build commands through `afs-run`, validate the handoff/return and repository scope, and only then complete the ticket.
