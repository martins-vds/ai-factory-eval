# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:20:11+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:24:00+00:00 | dialogs-red | 2 | 1.38 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `313a6d39f55ffb69` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-22T17:25:50+00:00 | dialogs-green | 0 | 4.45 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e3df911906c5f7a4` |  |  |
| 2026-11-22T17:26:09+00:00 | ui-check | 0 | 0.76 | `python .migration/harness/tools/check_ui.py` | `cb351229e5fed564` |  | gate=ui scope="templates changed since c396c044629bed0c19e3ff25279bf6319cd54ac4" templates=4 findings=0 |
| 2026-11-22T17:26:13+00:00 | dashboard-regression | 0 | 5.42 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `e1d43aa82c6ef89e` |  |  |
| 2026-11-22T17:27:20+00:00 | ruff-check | 0 | 0.04 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T17:27:20+00:00 | ruff-format | 1 | 0.04 | `ruff format --check` | `ce253605f2e5211f` | 112 \|     assert updated.route_specification.destination.unlocode.value == 'USNYC' |  |
| 2026-11-22T17:27:35+00:00 | ruff-format-final | 1 | 0.02 | `ruff format --check` | `40be7a28f8db9bca` |  |  |
| 2026-11-22T17:27:36+00:00 | ruff-check-final | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T17:27:41+00:00 | focused-tests | 0 | 5.54 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `d3ba7c636ccd26cf` |  |  |
