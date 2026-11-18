# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:51:28+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:55:04+00:00 | route-ui-red | 4 | 2.74 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_page_displays_candidate_count_and_numbered_itinerary_legs` | `585a5c6b6d30d592` | ERROR: found no collectors for /home/runner/work/ai-factory-eval/ai-factory-eval/tests/booking/interfaces/test_route_sel |  |
| 2026-11-18T12:55:56+00:00 | route-ui-green-1 | 1 | 2.14 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_page_displays_candidate_count_and_numbered_itinerary_legs` | `a43723a6cb65c1ec` | assert response.status_code == 200 |  |
| 2026-11-18T12:56:11+00:00 | route-ui-green-1 | 0 | 2.0 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_page_displays_candidate_count_and_numbered_itinerary_legs` | `73e52fbff0780f58` |  |  |
| 2026-11-18T12:56:27+00:00 | route-assignment-red | 0 | 2.11 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_assigning_candidate_redirects_to_details_and_persists_that_itinerary` | `cd7f1ce099caada6` |  |  |
| 2026-11-18T12:56:41+00:00 | route-ui-focused | 0 | 3.32 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `f3b1ddbe0b0712d6` |  |  |
| 2026-11-18T12:57:21+00:00 | route-ui-focused | 0 | 4.24 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `8fc475d7fcefb5b3` |  |  |
| 2026-11-18T12:57:54+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:57:54+00:00 | build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T12:57:54+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:57:54+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `86a46df0b248ec22` | 119 \|     assert all(candidate.legs for candidate in candidates) |  |
| 2026-11-18T12:57:54+00:00 | idiom-layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:57:55+00:00 | idiom-ui | 0 | 0.44 | `python .migration/harness/tools/check_ui.py` | `9043338b656cf2e0` |  | gate=ui scope="templates changed since 20bcb2322ba4084015a7fccbedf8f372ec75aac4" templates=3 findings=0 |
