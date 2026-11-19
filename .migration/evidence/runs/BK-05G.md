# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T13:55:05+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:59:57+00:00 | dialog-red-01 | 2 | 6.57 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `393c99da5d916289` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T14:01:13+00:00 | dialog-green-01 | 1 | 2.39 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0538ccf330c39542` | assert cargo is not None |  |
| 2026-11-19T14:01:25+00:00 | dialog-green-01 | 0 | 2.15 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `120e924bac659ca9` |  |  |
| 2026-11-19T14:02:42+00:00 | dialogs-targeted | 0 | 7.13 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `60f93a3101d33494` |  |  |
