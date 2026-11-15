# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T17:47:44+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T17:49:59+00:00 | export-red | 1 | 1.78 | `pytest -q tests/data_migration/test_export.py` | `9daf391cd463ab8d` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T17:50:33+00:00 | export-test | 0 | 1.5 | `pytest -q tests/data_migration/test_export.py` | `7b23e52dabef120c` |  |  |
