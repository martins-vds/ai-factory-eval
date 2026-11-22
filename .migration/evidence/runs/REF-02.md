# Run journal: REF-02

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T04:21:26+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:22:27+00:00 | behavior | 0 | 15.13 | `pytest -q tests/fees` | `734cd03d1959557c` |  |  |
| 2026-11-22T04:22:47+00:00 | build | 0 | 0.47 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-22T04:22:47+00:00 | idiom | 0 | 0.76 | `bash -c 'ruff check src config manage.py tests && ruff format --check src config manage.py tests && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `73fe731d5348c9e3` |  | gate=ui scope="templates changed since 89dbdc1c4e3d4492362d562f18fd0fcb85a398c2" templates=0 findings=0 |
| 2026-11-22T04:23:08+00:00 | crap | 0 | 17.63 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `6d1709a8c6ac4fdd` |  | gate=crap max=7.0 threshold=30 over=0 methods=46 |
| 2026-11-22T04:28:05+00:00 | mutation_changed | 0 | 295.52 | `python .migration/harness/tools/afs-mutation` | `536a01364ff6dc87` |  | gate=mutation score=1.000 threshold=0.8 killed=61 survived=0 files=2 base=89dbdc1c4e3d4492362d562f18fd0fcb85a398c2 |
| 2026-11-22T04:28:24+00:00 | regression | 0 | 15.2 | `pytest -q` | `3e79ee4ef5174e1e` |  |  |
