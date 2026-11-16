# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T20:35:47+00:00 | setup-probe | 0 | 0.01 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:37:10+00:00 | snapshot-check | 0 | 0.07 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T20:39:36+00:00 | focused-tests | 1 | 3.0 | `pytest -q tests/data_migration/test_invariants.py` | `797d7a559d8cebc4` | E               psycopg.errors.ForeignKeyViolation: insert or update on table "HandlingEvent" violates foreign key const |  |
| 2026-11-16T20:40:03+00:00 | focused-tests | 1 | 2.15 | `pytest -q tests/data_migration/test_invariants.py` | `96fb6ddcbf3ed42d` | assert movement.departure_time <= movement.arrival_time |  |
| 2026-11-16T20:40:16+00:00 | focused-tests | 0 | 2.1 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
| 2026-11-16T20:40:47+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:40:49+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T20:40:54+00:00 | idiom-ruff-check | 1 | 0.03 | `ruff check` | `ee7b6368f7bc2e4a` | 149 \|     assert any(len(itinerary) > 1 for itinerary in itineraries) |  |
| 2026-11-16T20:41:02+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T20:41:05+00:00 | idiom-format-check | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T20:42:07+00:00 | regression | 0 | 58.37 | `pytest -q` | `139a2c51610063a8` |  |  |
| 2026-11-16T20:43:08+00:00 | crap-coverage | 0 | 57.07 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `d19dcf0ae816d053` |  |  |
| 2026-11-16T20:43:11+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:43:14+00:00 | crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-16T20:43:19+00:00 | mutation-changed | 0 | 0.08 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
