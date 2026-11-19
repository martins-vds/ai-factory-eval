# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:14:06+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:17:36+00:00 | tdd-red-destination | 2 | 3.34 | `pytest -q tests/booking/interfaces/test_dialogs.py -k destination_dialog_excludes_origin_and_current_destination_without_mutating_locations` | `23ce79c7d0481ba1` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T18:18:01+00:00 | tdd-green-destination | 0 | 2.29 | `pytest -q tests/booking/interfaces/test_dialogs.py -k destination_dialog_excludes_origin_and_current_destination_without_mutating_locations` | `48d1e350f94062d9` |  |  |
