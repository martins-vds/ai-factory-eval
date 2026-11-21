# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T20:32:51+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:35:56+00:00 | route-tests-red | 2 | 1.04 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `d90b7782fcb3b73d` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
