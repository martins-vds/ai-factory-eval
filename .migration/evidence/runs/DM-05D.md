# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T21:39:22+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:42:24+00:00 | export-red | 1 | 2.72 | `pytest -q tests/data_migration/test_export.py` | `7ea949325fa35710` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-19T21:43:02+00:00 | export-green | 0 | 1.57 | `pytest -q tests/data_migration/test_export.py` | `a41ffd9d3e4191f8` |  |  |
