# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-20T23:48:40+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T23:51:05+00:00 | idiom | 1 | 0.07 | `ruff check` | `1c64809bd58354f6` |  |  |
| 2026-11-20T23:51:05+00:00 | build | 0 | 0.11 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T23:51:06+00:00 | build-manage-check | 0 | 0.63 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T23:51:06+00:00 | ui-check | 0 | 1.21 | `python .migration/harness/tools/check_ui.py` | `858dc8f0d875d783` |  | gate=ui scope="templates changed since 5bd801689b3e8b857aaf6610b5e570837c7b0beb" templates=1 findings=0 |
| 2026-11-20T23:51:09+00:00 | behavior | 0 | 4.54 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `0a291771bf2b50b6` | /home/runner/work/ai-factory-eval/ai-factory-eval:0: PytestWarning: Error when trying to teardown test databases: Progra |  |
| 2026-11-20T23:51:44+00:00 | idiom | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T23:51:45+00:00 | format-check | 0 | 0.03 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T23:52:07+00:00 | regression | 0 | 62.88 | `pytest -q` | `71dad5370c542f37` |  |  |
| 2026-11-20T23:52:13+00:00 | mutation_changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation` | `45567ab2cd87d32e` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=5bd801689b3e8b857aaf6610b5e570837c7b0beb |
| 2026-11-20T23:52:13+00:00 | layers | 0 | 0.22 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-20T23:53:24+00:00 | crap | 0 | 71.97 | `sh -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `be2163feab3862ef` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-20T23:56:00+00:00 | behavior | 0 | 4.7 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `b5d89dbc0a7ba7f4` |  |  |
| 2026-11-20T23:56:12+00:00 | idiom | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T23:56:12+00:00 | format-check | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T23:56:51+00:00 | mutation_changed | 0 | 0.14 | `python .migration/harness/tools/afs-mutation` | `45567ab2cd87d32e` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=5bd801689b3e8b857aaf6610b5e570837c7b0beb |
| 2026-11-20T23:57:15+00:00 | regression | 0 | 63.36 | `pytest -q` | `950df45bcf3a2061` |  |  |
| 2026-11-20T23:59:37+00:00 | behavior | 0 | 4.62 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `1cb8558b250f917d` |  |  |
