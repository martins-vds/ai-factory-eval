# Run journal: REF-20261122-ADMIN-LIVE-MAP

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T22:46:41+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T22:47:27+00:00 | behavior-before-refactor | 0 | 4.77 | `pytest -q tests/cargo/interfaces/test_admin_live_map_data.py` | `4586ecf3fb9d1b57` |  |  |
| 2026-11-22T22:48:18+00:00 | behavior-after-extraction-targeted | 0 | 3.12 | `pytest -q tests/cargo/interfaces/test_admin_live_map_data.py` | `3b03224376981219` |  |  |
