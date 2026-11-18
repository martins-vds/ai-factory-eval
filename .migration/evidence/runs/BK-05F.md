# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:40:41+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:45:42+00:00 | route-ui-red | 2 | 2.44 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `ffa42666eeae0547` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-18T12:46:20+00:00 | route-ui-populated | 0 | 1.97 | `pytest -q tests/booking/interfaces/test_route_selection.py -k route_page_renders_candidate_properties_and_numbered_legs` | `859bfef21b8bd45f` |  |  |
| 2026-11-18T12:47:07+00:00 | itinerary-branches | 1 | 2.43 | `pytest -q tests/booking/interfaces/test_route_selection.py -k select_itinerary` | `9622a3b5152acd53` | assert response.status_code == 200 |  |
| 2026-11-18T12:47:18+00:00 | itinerary-branches-fixed | 0 | 2.38 | `pytest -q tests/booking/interfaces/test_route_selection.py -k select_itinerary` | `5a4c4f51d8231da2` |  |  |
| 2026-11-18T12:47:23+00:00 | assignment-red | 1 | 2.02 | `pytest -q tests/booking/interfaces/test_route_selection.py -k assigning_candidate` | `c9e60655a9c55f0c` | >       assert token is not None |  |
| 2026-11-18T12:48:12+00:00 | route-ui-tests | 0 | 3.59 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3eae56deae2700cc` |  |  |
