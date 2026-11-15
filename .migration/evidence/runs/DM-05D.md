# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T20:14:56+00:00 | export-red | 1 | 4.14 | `pytest -q tests/data_migration/test_export.py` | `e950bbb73cec134e` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T20:15:29+00:00 | export-focused | 0 | 1.97 | `pytest -q tests/data_migration/test_export.py` | `67ecf94f55b8e441` |  |  |
| 2026-11-15T20:15:59+00:00 | export-focused-final | 0 | 2.04 | `pytest -q tests/data_migration/test_export.py` | `8f6abe38f9b13362` |  |  |
