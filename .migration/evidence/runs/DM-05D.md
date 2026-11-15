# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T13:42:32+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T13:44:28+00:00 | export-red | 1 | 1.7 | `pytest -q tests/data_migration/test_export.py` | `ddf8bdfc3bb92e4c` | E               KeyError: 'export_data_snapshot' |  |
