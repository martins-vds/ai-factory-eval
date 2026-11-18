# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:33:05+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:40:19+00:00 | behavior-red | 2 | 2.21 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `96d189e2c964cca8` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:41:42+00:00 | behavior-dialogs | 0 | 2.88 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a69fad2d38f69472` |  |  |
| 2026-11-18T12:42:06+00:00 | format-probe | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `8aecc9c52475f917` | 91  \|     assert first_options == second_options |  |
| 2026-11-18T12:42:19+00:00 | behavior-dialogs-formatted | 0 | 2.73 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `82f8b15bda752832` |  |  |
| 2026-11-18T12:42:19+00:00 | ruff-check-probe | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:42:19+00:00 | format-check-probe | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-18T12:42:19+00:00 | ui-check-probe | 0 | 0.26 | `python .migration/harness/tools/check_ui.py` | `d7c99a97f806b1f4` |  | gate=ui scope="templates changed since 9b190a54b0f0e1fcba9c9daa4ad85ce07f4c27c9" templates=3 findings=0 |
