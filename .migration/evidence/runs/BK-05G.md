# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T05:55:03+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T05:59:19+00:00 | focused-red | 2 | 1.33 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8fc2cc9247cc46e4` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-16T06:00:07+00:00 | focused-green | 1 | 4.18 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `47628a6ca7165cac` | assert original is not None |  |
| 2026-11-16T06:00:23+00:00 | focused-green | 0 | 4.26 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ad8923c4cd1a061f` |  |  |
| 2026-11-16T06:00:51+00:00 | bk05e-regression | 0 | 3.08 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/application/test_specification.py` | `b0e7f87e607a47de` |  |  |
| 2026-11-16T06:01:08+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T06:01:11+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T06:01:14+00:00 | idiom-ruff | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T06:01:17+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `3d056a9d156f64e3` | -     assert updated.route_specification.arrival_deadline == original.route_specification.arrival_deadline |  |
| 2026-11-16T06:01:33+00:00 | idiom-format | 1 | 0.01 | `ruff format --check` | `f7211c5350a6c30c` |  |  |
| 2026-11-16T06:01:46+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T06:02:13+00:00 | focused-dialogs | 0 | 5.68 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `b527882c5de54f21` |  |  |
| 2026-11-16T06:02:26+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T06:02:29+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T06:03:34+00:00 | behavior-suite | 0 | 61.47 | `pytest -q` | `75de2da7cc381e63` |  |  |
