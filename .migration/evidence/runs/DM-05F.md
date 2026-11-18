# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T03:00:24+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:02:57+00:00 | snapshot-help | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot --help` | `387e1fc810d4925d` |  |  |
| 2026-11-18T03:03:02+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-18T03:04:28+00:00 | invariants-red-green | 1 | 3.48 | `pytest -q tests/data_migration/test_invariants.py` | `256ce0fddfe08e29` | assert cargoes |  |
| 2026-11-18T03:04:48+00:00 | invariants | 0 | 1.48 | `pytest -q tests/data_migration/test_invariants.py` | `8dcd4ff2b182559e` |  |  |
| 2026-11-18T03:05:00+00:00 | idiom-ruff-check | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `5249f3f465c70822` | 209 \|             assert movement.departure_time <= movement.arrival_time |  |
| 2026-11-18T03:05:09+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:05:09+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-18T03:05:40+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:05:41+00:00 | build-check | 0 | 0.26 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T03:05:41+00:00 | idiom-ruff-check-all | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:05:41+00:00 | idiom-ruff-format-all | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T03:05:41+00:00 | idiom-layers | 0 | 0.1 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T03:05:41+00:00 | idiom-ui | 0 | 0.29 | `python .migration/harness/tools/check_ui.py` | `2e16617a69bea314` |  | gate=ui scope="templates changed since 01f1f08050b982e5e0fdd5b4e3dfb6bfaec9417f" templates=0 findings=0 |
| 2026-11-18T03:05:43+00:00 | behavior | 0 | 1.39 | `pytest -q tests/data_migration/test_invariants.py` | `b72ff9de67279024` |  |  |
| 2026-11-18T03:06:16+00:00 | regression | 0 | 30.18 | `pytest -q` | `c6009d11bf881c29` |  |  |
| 2026-11-18T03:07:04+00:00 | crap-coverage | 0 | 27.41 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `23981a3f6865bf6c` |  |  |
| 2026-11-18T03:07:04+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:07:04+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T03:07:11+00:00 | mutation-changed | 0 | 0.06 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T03:09:16+00:00 | build-compile-final | 0 | 0.02 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:09:16+00:00 | build-check-final | 0 | 0.22 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T03:09:16+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:09:16+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T03:09:16+00:00 | idiom-layers-final | 0 | 0.08 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T03:09:17+00:00 | idiom-ui-final | 0 | 0.26 | `python .migration/harness/tools/check_ui.py` | `2e16617a69bea314` |  | gate=ui scope="templates changed since 01f1f08050b982e5e0fdd5b4e3dfb6bfaec9417f" templates=0 findings=0 |
| 2026-11-18T03:09:18+00:00 | behavior-final | 0 | 1.3 | `pytest -q tests/data_migration/test_invariants.py` | `6d62fa340acc13b4` |  |  |
| 2026-11-18T03:09:45+00:00 | regression-final | 0 | 27.05 | `pytest -q` | `7415a64ef26152e6` |  |  |
| 2026-11-18T03:10:12+00:00 | crap-coverage-final | 0 | 27.15 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `e9fe6061fb781d37` |  |  |
| 2026-11-18T03:10:12+00:00 | crap-lizard-final | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:10:12+00:00 | crap-score-final | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T03:10:12+00:00 | mutation-changed-final | 0 | 0.06 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
