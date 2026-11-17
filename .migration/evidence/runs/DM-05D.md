# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-17T21:45:34+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:47:43+00:00 | export-red | 1 | 2.63 | `python -m pytest -q tests/data_migration/test_export.py` | `6b587924d2c066e0` | E               KeyError: 'export_data_snapshot' |  |
