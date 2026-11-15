# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T23:45:04+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T23:47:49+00:00 | test-first-dialogs | 2 | 3.7 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a7335d5a4a48b317` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-15T23:48:27+00:00 | dialogs-targeted | 1 | 4.29 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0a200da8bea8d468` | assert cargo is not None |  |
| 2026-11-15T23:48:45+00:00 | dialogs-debug | 1 | 2.35 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_shows_current_values_and_stable_filtered_options --showlocals` | `a6c03150ee718050` | assert cargo is not None |  |
| 2026-11-15T23:49:05+00:00 | dialogs-targeted | 1 | 4.27 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `015c5b11c4c6b84e` | assert cargo is not None |  |
| 2026-11-15T23:49:17+00:00 | dialogs-targeted | 0 | 4.32 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e4429539cf6c68d2` |  |  |
| 2026-11-15T23:49:43+00:00 | behavior-targeted | 0 | 5.42 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `ef336270381afd6c` |  |  |
| 2026-11-15T23:49:47+00:00 | idiom | 1 | 0.06 | `bash -c 'ruff check && ruff format --check'` | `b6ada98b1ee58c13` | 109 \|                 except LookupError as error: |  |
| 2026-11-15T23:51:56+00:00 | build | 0 | 0.44 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-15T23:53:03+00:00 | behavior | 0 | 63.32 | `pytest -q` | `68b23bbb432fa2d5` |  |  |
| 2026-11-15T23:53:07+00:00 | idiom | 1 | 0.03 | `bash -c 'ruff check && ruff format --check'` | `3adc8dd5dcaabe78` |  |  |
