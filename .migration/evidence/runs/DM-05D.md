# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T15:03:09+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T15:06:05+00:00 | export-red | 1 | 2.4 | `pytest -q tests/data_migration/test_export.py` | `6067e86239bf77c9` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T15:07:01+00:00 | export-focused | 0 | 1.85 | `pytest -q tests/data_migration/test_export.py` | `407df310e417114f` |  |  |
