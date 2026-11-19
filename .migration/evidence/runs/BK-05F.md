# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T21:38:57+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:42:35+00:00 | route-tests-red | 2 | 2.22 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `5b1981da916f2868` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
