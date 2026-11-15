# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T23:45:13+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T23:48:36+00:00 | invariants-red | 1 | 4.13 | `pytest -q tests/data_migration/test_invariants.py` | `6b98c95884586e1a` | E               psycopg.errors.ForeignKeyViolation: insert or update on table "HandlingEvent" violates foreign key const |  |
| 2026-11-15T23:48:53+00:00 | invariants-red-rerun | 0 | 2.11 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
