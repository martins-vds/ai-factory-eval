## Handoff — afs-migrator · 2026-11-21T13:22:09Z
**State:** blocked · **Branch / PR:** `copilot/dm-05d-export-data-snapshot-c7a11f1d-fcfa-4f16-a22f-06173716f0ce` / PR not found · **Last commit:** `39f5cdc4`

### Done
- Setup passed at source SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`; the snapshot check passed with 7 tables and 0 problems (`.migration/evidence/runs/DM-05D.md`).
- Implemented the mapping-driven exporter and `export_data_snapshot` command; the focused test file passes 20 tests.
- Build checks passed: `compileall` and `manage.py check` (exit 0).
- A full test run passed 420 tests before the later edge-case tests were added. Ruff and CRAP gates passed before those test-only additions; CRAP max was 26.0.
- CodeQL found 0 alerts; secret scanning found no secrets in changed code/tests.
- The first changed-code mutation run scored 0.659 (54 killed, 28 survived); survivor diffs are in `.migration/evidence/mutants/DM-05D.md`.

### Remaining
- [ ] Diagnose why the mutation worker's copied workspace cannot select `test_export_rejects_invalid_mapping`, although local `pytest --collect-only` selects its 12 parametrized cases.
- [ ] Rerun the default changed-code mutation gate and meet the 0.80 threshold; then review any remaining survivors.
- [ ] Rerun the full suite and final build, idiom, and CRAP gates after the expanded tests.
- [ ] Export and reconcile the validated snapshot, keeping exported rows outside the repository.
- [ ] Complete return validation and final checks.

### Decisions made
- No new data decisions; the approved mapping and rulings were left unchanged.

### Blockers / questions
- The migration-contract stop rule fired after two honest mutation attempts failed with the same worker-selector error. Do not retry mutation again until the selector/workspace issue is understood.

### Failing commands
- `python .migration/harness/tools/afs-mutation` → exit 1, score 0.659; see `.migration/runs/DM-05D/20261121T131533700958Z-mutation-changed.log:1-3`.
- `python .migration/harness/tools/afs-mutation` → exit 2, test selector not found; see `.migration/runs/DM-05D/20261121T131816362214Z-mutation-changed.log:1-8`.
- `python .migration/harness/tools/afs-mutation` → exit 2, same selector error; see `.migration/runs/DM-05D/20261121T131939391639Z-mutation-changed.log:1-8`.

### Next step for the next session
Run `afs-setup-check`, then inspect how `afs-mutation` builds its coverage-selected test IDs in the copied workspace; resolve that mismatch before rerunning the mutation gate.
