# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T21:38:57+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:42:35+00:00 | route-tests-red | 2 | 2.22 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `5b1981da916f2868` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-19T21:44:11+00:00 | route-tests-green-1 | 0 | 3.65 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `f59ca3387342dfc0` |  |  |
| 2026-11-19T21:44:52+00:00 | route-tests-green-2 | 0 | 4.49 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `36e16de7f4d22ddf` |  |  |
| 2026-11-19T21:45:08+00:00 | route-ruff-check | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:45:10+00:00 | route-ruff-format | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `f8044c57ecc8352c` | 143 \|     assert 'Itinerary' in details_response.content.decode() |  |
| 2026-11-19T21:45:15+00:00 | route-ruff-format-fix | 0 | 0.01 | `ruff format src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `96a977f329ec3c59` |  |  |
| 2026-11-19T21:45:23+00:00 | route-tests-final-targeted | 0 | 4.48 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `1cb8558b250f917d` |  |  |
| 2026-11-19T21:45:26+00:00 | route-ui-check | 0 | 0.45 | `python .migration/harness/tools/check_ui.py` | `9cf1220ce5965a3f` |  | gate=ui scope="templates changed since 6d29ae7f70131c9eb6ea6964c5eacb3650352052" templates=3 findings=0 |
