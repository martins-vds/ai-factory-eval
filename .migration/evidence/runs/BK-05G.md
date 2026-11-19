# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T13:47:37+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:50:51+00:00 | behavior-red | 2 | 3.05 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `d1e6b065bece3242` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T13:51:45+00:00 | behavior-dialogs | 1 | 4.5 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7e3b8f1e612472c7` | assert 'CNHKG' not in options |  |
| 2026-11-19T13:52:00+00:00 | behavior-dialogs | 0 | 4.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `132efd337b0c8ab8` |  |  |
| 2026-11-19T13:52:36+00:00 | lint-check | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T13:52:36+00:00 | format-check | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `6d0e33c9f94032e6` | 99  \|     assert updated.route_specification.origin == original.route_specification.origin |  |
| 2026-11-19T13:53:40+00:00 | behavior-dialogs-final | 0 | 4.28 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c8834e6ba7bf08dd` |  |  |
| 2026-11-19T13:53:40+00:00 | layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T13:53:40+00:00 | ui-check | 0 | 0.5 | `python .migration/harness/tools/check_ui.py` | `06b017a801dbbc41` |  | gate=ui scope="templates changed since f4a321e32b3e9774e62d6e26e215bb713d950221" templates=2 findings=0 |
