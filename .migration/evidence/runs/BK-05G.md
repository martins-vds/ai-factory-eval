# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T13:36:37+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:40:33+00:00 | red-destination-dialog | 2 | 0.78 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2237198fd9734b3c` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:44:31+00:00 | green-destination-initial | 0 | 1.25 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `38e13be45293b3a0` |  |  |
| 2026-11-18T13:44:47+00:00 | red-invalid-destination | 1 | 1.27 | `pytest -q tests/booking/interfaces/test_dialogs.py -k rejects_origin` | `c4d6d8a84c23ee02` | assert response.status_code == 200 |  |
| 2026-11-18T13:45:10+00:00 | green-destination-boundary | 0 | 1.48 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ae472916d0d50dc9` |  |  |
| 2026-11-18T13:46:06+00:00 | red-deadline-initial | 2 | 0.57 | `pytest -q tests/booking/interfaces/test_dialogs.py -k deadline_dialog` | `3280b595539d8d38` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:46:21+00:00 | green-deadline-initial | 2 | 0.54 | `pytest -q tests/booking/interfaces/test_dialogs.py -k deadline_dialog` | `2d400fe10c1aba72` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:46:29+00:00 | green-deadline-initial | 0 | 1.28 | `pytest -q tests/booking/interfaces/test_dialogs.py -k deadline_dialog` | `772d478cfb65248c` |  |  |
| 2026-11-18T13:46:40+00:00 | red-deadline-parse-error | 1 | 1.31 | `pytest -q tests/booking/interfaces/test_dialogs.py -k parse_error` | `4f5fb2d042b7759d` | assert cargo is not None |  |
| 2026-11-18T13:46:58+00:00 | red-deadline-success | 1 | 1.38 | `pytest -q tests/booking/interfaces/test_dialogs.py -k updates_deadline` | `f7d8842ef45cf804` | assert cargo is not None |  |
| 2026-11-18T13:47:18+00:00 | green-deadline-flows | 0 | 2.29 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8c6fecfc1b2d4cb4` |  |  |
