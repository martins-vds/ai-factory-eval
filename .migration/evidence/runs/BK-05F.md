# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T01:09:21+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T01:10:27+00:00 | route-selection-red | 2 | 2.76 | `rtk pytest -q tests/booking/interfaces/test_route_selection.py` | `9bfb4a900cb1a607` | 1. [ERROR] collecting tests/booking/interfaces/test_route_selection.py |  |
| 2026-11-21T01:10:56+00:00 | route-selection-targeted | 1 | 2.64 | `rtk pytest -q tests/booking/interfaces/test_route_selection.py` | `b99c06189aee603b` | Pytest: 0 passed, 3 failed in 2.04s |  |
| 2026-11-21T01:11:21+00:00 | route-selection-targeted | 0 | 2.47 | `rtk pytest -q tests/booking/interfaces/test_route_selection.py` | `4ce02b9f3b76d172` |  |  |
