# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T20:35:47+00:00 | setup-probe | 0 | 0.01 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:37:10+00:00 | snapshot-check | 0 | 0.07 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T20:39:36+00:00 | focused-tests | 1 | 3.0 | `pytest -q tests/data_migration/test_invariants.py` | `797d7a559d8cebc4` | E               psycopg.errors.ForeignKeyViolation: insert or update on table "HandlingEvent" violates foreign key const |  |
| 2026-11-16T20:40:03+00:00 | focused-tests | 1 | 2.15 | `pytest -q tests/data_migration/test_invariants.py` | `96fb6ddcbf3ed42d` | assert movement.departure_time <= movement.arrival_time |  |
| 2026-11-16T20:40:16+00:00 | focused-tests | 0 | 2.1 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
