# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-20T00:34:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:41:23+00:00 | red-route-selection | 2 | 3.45 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `30118c578d2b7565` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-20T00:42:43+00:00 | route-selection-tests | 0 | 4.55 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `48deeaacfc209ce4` |  |  |
| 2026-11-20T00:43:28+00:00 | route-selection-tests | 0 | 4.72 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `4912e2b6b711d5ba` |  |  |
| 2026-11-20T00:43:34+00:00 | ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:43:39+00:00 | ruff-format-check | 1 | 0.02 | `ruff format --check` | `20f5a8ba78c18ce5` | 42 \|                     error='Select a route shown on this page.', |  |
| 2026-11-20T00:43:55+00:00 | ruff-format-check | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
