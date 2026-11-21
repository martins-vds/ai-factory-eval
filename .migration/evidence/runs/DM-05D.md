# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T23:43:34+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:45:54+00:00 | export-tests-red | 1 | 2.32 | `pytest -q tests/data_migration/test_export.py` | `dd0f0098aa02026b` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-21T23:46:17+00:00 | export-tests | 0 | 2.01 | `pytest -q tests/data_migration/test_export.py` | `23aad8c8d530c077` |  |  |
