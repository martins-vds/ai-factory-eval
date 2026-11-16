# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:35:51+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:39:19+00:00 | behavior-dialogs-red | 2 | 2.06 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c31cbd21411297e4` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-16T20:40:04+00:00 | behavior-dialogs | 0 | 2.52 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e64b59c82423fe0a` |  |  |
| 2026-11-16T20:40:41+00:00 | behavior-dialog-dashboard | 0 | 3.0 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `833d0e0e1598f02f` |  |  |
| 2026-11-16T20:41:30+00:00 | build-compileall | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:41:35+00:00 | build-django-check | 0 | 0.24 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T20:41:39+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `45b5306885a0f2c2` | Found 1 error. |  |
| 2026-11-16T20:41:47+00:00 | idiom-ruff-check-rerun | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T20:41:51+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `eac1fddb949f359f` | 95  \|     assert ( |  |
| 2026-11-16T20:42:02+00:00 | idiom-ruff-format-rerun | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T20:42:08+00:00 | behavior-dialog-dashboard-final | 0 | 3.01 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `b5877acbd4d8092e` |  |  |
| 2026-11-16T20:42:47+00:00 | regression | 0 | 34.7 | `pytest -q` | `b774c8084ae098a5` |  |  |
| 2026-11-16T20:43:49+00:00 | crap-coverage | 0 | 33.11 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `aba23434cc77ed74` |  |  |
| 2026-11-16T20:44:01+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:44:04+00:00 | crap-threshold | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0e71f99bcc37d642` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-16T20:44:08+00:00 | mutation-changed | 0 | 0.05 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
