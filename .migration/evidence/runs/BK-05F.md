# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:51:28+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:55:04+00:00 | route-ui-red | 4 | 2.74 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_page_displays_candidate_count_and_numbered_itinerary_legs` | `585a5c6b6d30d592` | ERROR: found no collectors for /home/runner/work/ai-factory-eval/ai-factory-eval/tests/booking/interfaces/test_route_sel |  |
