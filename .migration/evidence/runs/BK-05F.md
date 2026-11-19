# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T18:14:00+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:17:32+00:00 | tests-red | 2 | 6.71 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `e4c9bca63593996c` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-19T18:18:19+00:00 | tests-targeted | 0 | 3.51 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3eae56deae2700cc` |  |  |
