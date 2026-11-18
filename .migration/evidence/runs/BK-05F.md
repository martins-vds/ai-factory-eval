# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:40:41+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:45:42+00:00 | route-ui-red | 2 | 2.44 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `ffa42666eeae0547` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-18T12:46:20+00:00 | route-ui-populated | 0 | 1.97 | `pytest -q tests/booking/interfaces/test_route_selection.py -k route_page_renders_candidate_properties_and_numbered_legs` | `859bfef21b8bd45f` |  |  |
