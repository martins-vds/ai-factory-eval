# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T13:50:26+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:56:27+00:00 | tests-red | 2 | 2.72 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `776532920662f532` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-18T13:57:01+00:00 | tests-focused | 1 | 4.39 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `5b07792890be6604` | assert response.status_code == 200 |  |
| 2026-11-18T13:57:18+00:00 | tests-focused-2 | 0 | 4.55 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `c3b75cb084e5bca8` |  |  |
