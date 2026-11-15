# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T02:39:37+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T02:42:27+00:00 | export-red | 1 | 3.25 | `pytest -q tests/data_migration/test_export.py` | `c1833eae99e0edee` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T02:43:18+00:00 | export-tests | 0 | 1.02 | `pytest -q tests/data_migration/test_export.py` | `c45b5c446e3c4c9b` |  |  |
| 2026-11-15T02:43:40+00:00 | data-migration-tests | 0 | 3.11 | `pytest -q tests/data_migration/` | `1b92966aec6aadb0` |  |  |
