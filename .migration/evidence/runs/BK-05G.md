# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T07:07:59+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T07:08:12+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T07:10:23+00:00 | bk05e-dashboard-regression | 0 | 2.53 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `6343dd31090b1c8a` |  |  |
| 2026-11-15T07:13:13+00:00 | destination-dialog-red | 4 | 0.52 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_shows_current_values_and_stable_filtered_options` | `4ecd2ae60706e49b` | ERROR: found no collectors for /home/runner/work/ai-factory-eval/ai-factory-eval/tests/booking/interfaces/test_dialogs.p |  |
| 2026-11-15T07:13:57+00:00 | destination-dialog-green | 0 | 1.32 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_shows_current_values_and_stable_filtered_options` | `7ed2738ac3dcd8f9` |  |  |
