# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T13:08:32+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:12:10+00:00 | route-selection-red | 2 | 2.79 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3c22b3dd08b5d414` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-21T13:12:52+00:00 | route-selection-green | 1 | 1.62 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `a65a638d623bdce2` | E       AttributeError: 'Repository' object has no attribute 'upsert' |  |
| 2026-11-21T13:13:00+00:00 | route-selection-green | 0 | 1.74 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `d6ffdb45571cf2ef` |  |  |
| 2026-11-21T13:13:13+00:00 | route-selection-ruff | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:13:13+00:00 | route-selection-format | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-21T13:13:14+00:00 | route-selection-ui | 0 | 0.46 | `python .migration/harness/tools/check_ui.py` | `2fab799a37e17776` |  | gate=ui scope="templates changed since a135db8cd96803a5692cc2c30e5842fe1c87893c" templates=3 findings=0 |
| 2026-11-21T13:13:14+00:00 | route-selection-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
