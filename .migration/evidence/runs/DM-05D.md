# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T23:44:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T23:47:44+00:00 | tdd-roundtrip-red | 1 | 1.91 | `pytest -q tests/data_migration/test_export.py` | `21ae232261d0cd1c` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T23:48:19+00:00 | tdd-roundtrip-green | 0 | 1.64 | `pytest -q tests/data_migration/test_export.py` | `a2ff0172c1450afa` |  |  |
