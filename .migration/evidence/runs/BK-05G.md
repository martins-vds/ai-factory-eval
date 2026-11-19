# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:17:15+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:21:04+00:00 | test-table-dialog-controls-red | 1 | 3.38 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_exposes_dialog_controls_without_changing_route_link` | `f9d2fa26402f9a10` | assert response.status_code == 200 |  |
| 2026-11-19T18:21:44+00:00 | test-table-dialog-controls-green | 0 | 1.59 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_exposes_dialog_controls_without_changing_route_link` | `941ba30613647e4a` |  |  |
