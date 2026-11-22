# Run journal: REF-01

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T04:22:42+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:23:28+00:00 | refactor-red | 2 | 3.93 | `pytest -q tests/data_migration/test_export.py` | `c2ec8b1d2cb022ec` | _____________ ERROR collecting tests/data_migration/test_export.py _____________ |  |
| 2026-11-22T04:23:49+00:00 | behavior-focused | 0 | 2.25 | `pytest -q tests/data_migration/test_export.py` | `cd1a1d7624dff51b` |  |  |
