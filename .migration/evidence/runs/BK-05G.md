# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T20:33:09+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:37:05+00:00 | dialogs-red | 2 | 2.94 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8a93686ce1817765` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-21T20:38:24+00:00 | dialogs-view-red | 1 | 5.34 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7bf2c755ba5deb61` | >       assert 'Change destination' in content |  |
| 2026-11-21T20:39:13+00:00 | dialogs-targeted | 0 | 4.76 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c9601526caea5818` |  |  |
| 2026-11-21T20:39:59+00:00 | dialogs-targeted | 0 | 6.78 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `75be333015baf968` |  |  |
| 2026-11-21T20:40:04+00:00 | ui-check | 0 | 0.67 | `python .migration/harness/tools/check_ui.py` | `af6cca03828672e0` |  | gate=ui scope="templates changed since b491ff4233bc289cdda3c2c7fa6163c4a55acd78" templates=4 findings=0 |
| 2026-11-21T20:40:07+00:00 | ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:40:09+00:00 | ruff-format | 1 | 0.02 | `ruff format --check` | `ca6ca915a5f83088` | 76 \|     assert 'AUMEL' not in option_values |  |
| 2026-11-21T20:40:16+00:00 | ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
