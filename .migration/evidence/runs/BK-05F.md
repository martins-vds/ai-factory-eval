# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T13:55:17+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:59:45+00:00 | test-route-selection-red | 2 | 2.37 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `db51e39c18a4bcbb` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-19T14:00:48+00:00 | test-route-selection-green-1 | 1 | 3.43 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `23de5dd1727cb689` | assert response.status_code == 200 |  |
| 2026-11-19T14:01:17+00:00 | test-route-selection-diagnose | 1 | 3.2 | `pytest -q --showlocals tests/booking/interfaces/test_route_selection.py` | `392be886ba60917a` | assert response.status_code == 200 |  |
| 2026-11-19T14:01:41+00:00 | test-route-candidate-context | 1 | 1.85 | `pytest -q --showlocals tests/booking/interfaces/test_route_selection.py::test_route_page_displays_cargo_candidate_count_and_numbered_connected_legs` | `d0414460d486bf64` | assert response.status_code == 200 |  |
| 2026-11-19T14:02:16+00:00 | test-route-selection-green-2 | 0 | 3.28 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `90dfd6d8ae1500b9` |  |  |
| 2026-11-19T14:03:21+00:00 | test-route-selection-green-3 | 0 | 3.22 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `a3012a2f86fa8e15` |  |  |
| 2026-11-19T14:04:17+00:00 | test-route-selection-focused | 0 | 3.61 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `abd94044373779af` |  |  |
