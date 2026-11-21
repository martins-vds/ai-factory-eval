# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T20:32:51+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:35:56+00:00 | route-tests-red | 2 | 1.04 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `d90b7782fcb3b73d` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-21T20:37:08+00:00 | route-tests-green | 0 | 2.93 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `bd07ca1614724377` |  |  |
| 2026-11-21T20:38:18+00:00 | route-tests-green2 | 0 | 2.95 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `bd07ca1614724377` |  |  |
| 2026-11-21T20:39:44+00:00 | candidate-selection-red | 1 | 1.79 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_candidate_assignment_redirects_to_cargo_details_and_renders_assigned_itinerary` | `862b1cbe7db9c20d` | >       assert len(candidate_tokens) == 2 |  |
| 2026-11-21T20:40:07+00:00 | invalid-selection-red | 1 | 1.81 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_invalid_candidate_token_displays_error_without_requesting_new_candidates` | `57a8cd0091cd99a1` | assert response.status_code == 400 |  |
| 2026-11-21T20:40:34+00:00 | route-tests-green3 | 1 | 3.31 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `8b2597ae5b374b99` | >       assert len(candidate_tokens) == 2 |  |
| 2026-11-21T20:40:51+00:00 | route-tests-green4 | 0 | 3.36 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `c3b32caa90fa5633` |  |  |
| 2026-11-21T20:41:14+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `91e813e913baf00f` |  |  |
| 2026-11-21T20:41:14+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `a3de3ea4a7638e81` |  |  |
| 2026-11-21T20:41:14+00:00 | idiom-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T20:41:15+00:00 | idiom-ui | 0 | 0.44 | `python .migration/harness/tools/check_ui.py` | `40d22036570507e9` |  | gate=ui scope="templates changed since 3e6a94a28aa0563b9ac475e7a4b4ef6821f8a516" templates=2 findings=0 |
| 2026-11-21T20:41:36+00:00 | route-tests-final | 0 | 3.32 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `9951aca7006aea4e` |  |  |
