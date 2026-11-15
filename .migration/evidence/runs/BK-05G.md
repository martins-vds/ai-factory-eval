# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T04:10:12+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T04:14:08+00:00 | dialogs-red | 2 | 2.81 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ffdd1ddeed459e44` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-15T04:15:34+00:00 | dialogs-targeted | 1 | 5.41 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `2332ecd1430113d8` | assert response.status_code == 200 |  |
| 2026-11-15T04:15:51+00:00 | dialogs-targeted-rerun | 0 | 5.4 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `b6a5cd39ed42b402` |  |  |
| 2026-11-15T04:17:02+00:00 | dialogs-targeted-final | 0 | 5.27 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `1d5afa49e57deda6` |  |  |
| 2026-11-15T04:17:13+00:00 | idiom-targeted | 1 | 0.03 | `bash -c 'ruff check && ruff format --check'` | `5a2a217322150078` | Found 1 error. |  |
| 2026-11-15T04:17:21+00:00 | idiom-targeted-rerun | 1 | 0.04 | `bash -c 'ruff check && ruff format --check'` | `b983592474d9c9e2` | 143 \|     assert cargo_after.route_specification.origin == cargo_before.route_specification.origin |  |
| 2026-11-15T04:17:28+00:00 | idiom-targeted-final | 0 | 0.02 | `bash -c 'ruff check && ruff format --check'` | `6a496cdbbfea65a9` |  |  |
| 2026-11-15T04:18:00+00:00 | build | 0 | 0.45 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-15T04:19:10+00:00 | behavior | 0 | 62.26 | `pytest -q` | `b1ead7b5f4bf6626` |  |  |
| 2026-11-15T04:20:15+00:00 | regression | 0 | 60.26 | `pytest -q` | `17257e666d03074f` |  |  |
| 2026-11-15T04:21:33+00:00 | crap | 0 | 71.58 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `1efba9669f6d7f9c` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
