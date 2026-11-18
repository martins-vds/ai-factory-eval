# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:32:58+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:36:00+00:00 | route-selection-red | 2 | 2.68 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `7afd4fc89a879bb2` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
