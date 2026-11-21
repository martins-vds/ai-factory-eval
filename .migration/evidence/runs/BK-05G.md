# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T18:53:06+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T18:57:28+00:00 | red-destination-initial | 4 | 2.68 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_shows_initial_values_and_stable_filtered_options` | `cd3278f3bdc38592` | ERROR: found no collectors for /home/runner/work/ai-factory-eval/ai-factory-eval/tests/booking/interfaces/test_dialogs.p |  |
| 2026-11-21T18:58:26+00:00 | behavior-dialog-initial | 0 | 3.17 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_shows_initial_values_and_stable_filtered_options tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_shows_cargo_route_fields_and_current_deadline` | `dfc416a005792190` |  |  |
