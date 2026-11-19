# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T13:47:33+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:51:33+00:00 | route-selection-red | 2 | 4.14 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `ab4a2ff3557c30c7` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-19T13:52:28+00:00 | route-selection-green | 1 | 2.74 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `c55ab1c5b2e7c66a` | assert response.status_code == 200 |  |
| 2026-11-19T13:52:44+00:00 | route-selection-focused | 0 | 2.57 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `9c904c5062f49259` |  |  |
