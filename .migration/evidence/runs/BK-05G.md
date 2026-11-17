# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:02:43+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:08:30+00:00 | table-red | 1 | 2.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7b46d3f486b7fc1a` | assert response.status_code == 200 |  |
| 2026-11-17T21:08:46+00:00 | table-green | 0 | 1.89 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bda5018250507163` |  |  |
| 2026-11-17T21:09:34+00:00 | dialogs-red | 2 | 0.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `618acd581f0d4fb6` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-17T21:10:16+00:00 | dialogs-green | 1 | 3.67 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `3b6301539b820179` | assert cargo is not None |  |
| 2026-11-17T21:10:30+00:00 | dialogs-green | 0 | 3.71 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `1d90be47c8a54e42` |  |  |
| 2026-11-17T21:10:51+00:00 | format-targeted | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `4256d9ffafcc5651` | 78  \|     assert options is not None |  |
| 2026-11-17T21:10:51+00:00 | lint-targeted | 1 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `8b8cac0ee788c878` | Found 1 error. |  |
| 2026-11-17T21:11:08+00:00 | lint-targeted | 1 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `b1bdc3426af7ab95` | Found 1 error. |  |
| 2026-11-17T21:11:08+00:00 | format-targeted | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `e6a09a1d999abf0e` | 78  \|     assert options is not None |  |
| 2026-11-17T21:11:12+00:00 | dialogs-green | 0 | 3.75 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6aae4cb3848b2348` |  |  |
| 2026-11-17T21:11:35+00:00 | format-diff | 1 | 0.01 | `ruff format --diff tests/booking/interfaces/test_dialogs.py` | `b832bf06efdfe148` | assert options is not None |  |
| 2026-11-17T21:11:35+00:00 | lint-diff | 1 | 0.01 | `ruff check --fix --diff tests/booking/interfaces/test_dialogs.py` | `708d97426db000a0` | Would fix 1 error. |  |
| 2026-11-17T21:11:43+00:00 | lint-targeted | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:11:43+00:00 | format-targeted | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `37d5885b4bb0016d` | 77 \|     assert options is not None |  |
| 2026-11-17T21:11:46+00:00 | dialogs-green | 0 | 3.82 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7ab97723726f01f7` |  |  |
| 2026-11-17T21:12:01+00:00 | lint-targeted | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:12:01+00:00 | format-targeted | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-17T21:12:04+00:00 | dialogs-green | 0 | 3.81 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ad4dc636c010c6b7` |  |  |
| 2026-11-17T21:15:02+00:00 | format-targeted | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-17T21:15:02+00:00 | lint-targeted | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:15:06+00:00 | dialogs-green | 0 | 3.79 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `1c569b590fa8576c` |  |  |
| 2026-11-17T21:16:06+00:00 | format-targeted | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-17T21:16:06+00:00 | lint-targeted | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:16:10+00:00 | dialogs-green | 0 | 4.34 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7e454276a0aa633e` |  |  |
| 2026-11-17T21:17:09+00:00 | build | 0 | 0.41 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-17T21:17:15+00:00 | idiom | 0 | 0.04 | `bash -c 'ruff check && ruff format --check'` | `6a496cdbbfea65a9` |  |  |
| 2026-11-17T21:18:09+00:00 | behavior | 0 | 48.95 | `pytest -q` | `0f5f7efce87440ed` |  |  |
| 2026-11-17T21:19:06+00:00 | crap | 0 | 50.54 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `799800fd07785b92` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-17T21:22:52+00:00 | mutation_changed | 1 | 140.04 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `db9ae17030bc14f7` | afs-mutation: FAILED score=0.739 threshold=0.8 killed=51 survived=18 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.739 threshold=0.8 killed=51 survived=18 files=1 base=origin/main |
| 2026-11-17T21:24:07+00:00 | lint-targeted | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:24:07+00:00 | format-targeted | 0 | 0.04 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-17T21:24:14+00:00 | dialogs-expanded | 0 | 7.1 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7a018cab076c8003` |  |  |
| 2026-11-17T21:24:41+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:28:02+00:00 | mutation-changed-expanded | 0 | 169.96 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `7e25745feae0cb8f` |  | gate=mutation score=0.923 threshold=0.8 killed=60 survived=5 files=1 base=origin/main |
| 2026-11-17T21:28:34+00:00 | idiom-targeted | 0 | 0.07 | `bash -c 'ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py && ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py'` | `afa20b27dacc9bf0` |  |  |
| 2026-11-17T21:28:41+00:00 | dialogs-survivor-coverage | 0 | 7.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6619cd4412327690` |  |  |
| 2026-11-17T21:31:31+00:00 | mutation-changed-final | 0 | 154.65 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `db8abfc7ddf263a1` |  | gate=mutation score=1.000 threshold=0.8 killed=65 survived=0 files=1 base=origin/main |
