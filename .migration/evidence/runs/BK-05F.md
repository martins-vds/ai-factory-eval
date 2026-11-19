# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T18:17:18+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:17:41+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:20:30+00:00 | tests-red | 2 | 2.31 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `f9ae0c1b351b3230` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-19T18:21:54+00:00 | tests-targeted | 1 | 1.45 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `cb12ebf8759e0dc0` | assert response.status_code == 200 |  |
| 2026-11-19T18:22:12+00:00 | tests-targeted | 0 | 1.32 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `2ec7ef7d45b9aad9` |  |  |
| 2026-11-19T18:22:51+00:00 | tests-targeted | 0 | 1.33 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `7fff5cb703d8bcd2` |  |  |
