# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T13:50:26+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:56:27+00:00 | tests-red | 2 | 2.72 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `776532920662f532` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-18T13:57:01+00:00 | tests-focused | 1 | 4.39 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `5b07792890be6604` | assert response.status_code == 200 |  |
| 2026-11-18T13:57:18+00:00 | tests-focused-2 | 0 | 4.55 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `c3b75cb084e5bca8` |  |  |
| 2026-11-18T13:59:03+00:00 | candidate-stability-red | 1 | 2.91 | `pytest -q tests/booking/interfaces/test_route_selection.py -k assignment_keeps` | `ffe045f00bd45b36` | assert assignment_response.status_code == 302 |  |
| 2026-11-18T13:59:42+00:00 | candidate-token-red | 1 | 3.97 | `pytest -q tests/booking/interfaces/test_route_selection.py -k 'assignment_keeps or assign_candidate or select_itinerary_renders'` | `22ba7a04c2b50554` | assert response.status_code == 200 |  |
| 2026-11-18T14:00:14+00:00 | tests-focused-3 | 0 | 5.24 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `08b0a643daff4600` |  |  |
| 2026-11-18T14:00:32+00:00 | tests-focused-4 | 0 | 5.83 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `5243c91bd206b0a0` |  |  |
| 2026-11-18T14:03:00+00:00 | idiom-ruff-check | 1 | 0.03 | `ruff check` | `794477ea1a59eb2d` | Found 1 error. |  |
| 2026-11-18T14:03:09+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T14:03:14+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T14:03:21+00:00 | idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T14:03:25+00:00 | idiom-ui | 0 | 0.53 | `python .migration/harness/tools/check_ui.py` | `d10fc1a749bf95c7` |  | gate=ui scope="templates changed since 46add748bf3d7705ba555495eaa7df98b4efd538" templates=3 findings=0 |
| 2026-11-18T14:04:15+00:00 | tests-focused-final | 0 | 5.43 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `23b853f8c249cc9f` |  |  |
| 2026-11-18T14:07:44+00:00 | tests-template-review | 0 | 5.39 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `aff3af738e4765da` |  |  |
| 2026-11-18T14:07:50+00:00 | idiom-ui-final | 0 | 0.53 | `python .migration/harness/tools/check_ui.py` | `df17627363e4fdab` |  | gate=ui scope="templates changed since 46add748bf3d7705ba555495eaa7df98b4efd538" templates=4 findings=0 |
