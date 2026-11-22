# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:27:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:31:09+00:00 | dialogs-red | 2 | 1.36 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8fc2cc9247cc46e4` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-22T17:32:06+00:00 | dialogs-targeted | 1 | 4.73 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `d312d746bed81c3f` | assert first_response.status_code == 200 |  |
| 2026-11-22T17:32:34+00:00 | dialogs-targeted | 1 | 4.75 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `04d9fbaee3bdf636` | assert cargo is not None |  |
| 2026-11-22T17:32:50+00:00 | dialogs-targeted | 0 | 4.67 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `3043b238ba5b8844` |  |  |
| 2026-11-22T17:33:26+00:00 | behavior-targeted | 0 | 5.88 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py tests/booking/application/test_specification.py` | `edc89db40b004151` |  |  |
