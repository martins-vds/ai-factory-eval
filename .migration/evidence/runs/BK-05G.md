# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:34:42+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:38:24+00:00 | dialogs-red-table | 1 | 2.79 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a202bd45c665cac4` | assert cargo is not None |  |
| 2026-11-20T00:38:46+00:00 | dialogs-green-table | 0 | 2.29 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `488b55d0b06d1251` |  |  |
| 2026-11-20T00:40:06+00:00 | dialogs-red-views | 2 | 1.08 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `b57025eeed794451` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-20T00:40:42+00:00 | dialogs-tests | 1 | 2.35 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0760d4a3a2c4c708` | _ ERROR at setup of test_not_routed_table_opens_destination_and_deadline_dialogs _ |  |
| 2026-11-20T00:40:56+00:00 | dialogs-tests | 0 | 6.63 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4aacc64bf85b7490` |  |  |
| 2026-11-20T00:41:10+00:00 | dashboard-regression | 0 | 7.9 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_dialogs.py` | `49bcda0ac892ac1c` |  |  |
| 2026-11-20T00:48:07+00:00 | dialogs-red-no-js | 1 | 7.24 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `f3790d4a842362c0` | assert cargo is not None |  |
| 2026-11-20T00:49:02+00:00 | dialogs-no-js-fallback | 0 | 7.11 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cd7bcc7d41fe3f3b` |  |  |
| 2026-11-20T00:49:14+00:00 | layers-check | 0 | 0.18 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-20T00:49:14+00:00 | ui-check | 0 | 0.73 | `python .migration/harness/tools/check_ui.py` | `16328f442d5b283e` |  | gate=ui scope="templates changed since c6d033992ff59d8640efed62f3b53589e26bd69f" templates=7 findings=0 |
| 2026-11-20T00:49:22+00:00 | focused-regression-final | 0 | 8.22 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_dialogs.py` | `c2150a10910a5d4f` |  |  |
| 2026-11-20T00:49:28+00:00 | ruff-format | 1 | 0.04 | `ruff format --check` | `2191be9d8cde1cf8` |  |  |
| 2026-11-20T00:49:28+00:00 | ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:49:38+00:00 | ruff-format | 0 | 0.03 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T00:49:46+00:00 | focused-regression-current | 0 | 8.13 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_dialogs.py` | `787245bc802e85eb` |  |  |
| 2026-11-20T00:50:30+00:00 | ruff-check-current | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:50:30+00:00 | ruff-format-current | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T00:50:38+00:00 | focused-regression-current | 0 | 8.91 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_dialogs.py` | `31076622912c294d` |  |  |
