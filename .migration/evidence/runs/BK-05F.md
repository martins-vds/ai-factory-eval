# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T13:08:32+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:12:10+00:00 | route-selection-red | 2 | 2.79 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3c22b3dd08b5d414` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
