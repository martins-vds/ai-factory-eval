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
| 2026-11-16T06:04:53+00:00 | crap-coverage | 0 | 59.86 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `e9c001b4acd89f6b` |  |  |
| 2026-11-16T06:04:57+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T06:05:01+00:00 | crap | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `bfee3b6a3acefaf6` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-16T06:08:30+00:00 | mutation-changed | 1 | 203.57 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `41fd5c8defbcc890` | afs-mutation: FAILED score=0.720 threshold=0.8 killed=59 survived=23 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.720 threshold=0.8 killed=59 survived=23 files=1 base=origin/main |
| 2026-11-16T06:09:57+00:00 | focused-mutant-coverage | 1 | 6.55 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ec098dd0578c9b21` | assert first.status_code == 200 |  |
| 2026-11-16T06:10:30+00:00 | focused-mutant-coverage | 0 | 6.62 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `44edd162ba024d43` |  |  |
| 2026-11-16T06:10:37+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T06:10:41+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T06:13:23+00:00 | mutation-changed | 0 | 158.81 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `773d5c838a221491` |  | gate=mutation score=0.986 threshold=0.8 killed=72 survived=1 files=1 base=origin/main |
| 2026-11-16T06:13:53+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T06:13:57+00:00 | build-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T06:15:04+00:00 | behavior-suite | 0 | 62.01 | `pytest -q` | `e0fb684151b1445a` |  |  |
| 2026-11-16T06:16:12+00:00 | crap-coverage | 0 | 61.84 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `1fbbed818539814f` |  |  |
| 2026-11-16T06:16:16+00:00 | crap-lizard | 0 | 0.17 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T06:16:20+00:00 | crap | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `38f05226bd6f9e64` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
