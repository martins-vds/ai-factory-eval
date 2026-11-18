# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T13:21:07+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:23:29+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-18T13:25:21+00:00 | invariants-tests | 0 | 3.63 | `pytest -q tests/data_migration/test_invariants.py` | `2adbb35b08f0583e` |  |  |
| 2026-11-18T13:25:40+00:00 | build-compileall | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:25:41+00:00 | build-django-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T13:25:45+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `a3cfeff3888b2f4a` | 204 \|         assert legs |  |
| 2026-11-18T13:26:04+00:00 | invariants-tests | 0 | 1.9 | `pytest -q tests/data_migration/test_invariants.py` | `846f06875c7c84ed` |  |  |
| 2026-11-18T13:26:04+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:26:04+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T13:26:05+00:00 | idiom-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:26:05+00:00 | idiom-ui | 0 | 0.39 | `python .migration/harness/tools/check_ui.py` | `617c55c57b113cf8` |  | gate=ui scope="templates changed since 884612afff7c2c399300b72816e2b6fd75be8054" templates=0 findings=0 |
| 2026-11-18T13:27:05+00:00 | regression | 0 | 45.99 | `pytest -q` | `919680e49af86164` |  |  |
| 2026-11-18T13:27:58+00:00 | crap-coverage | 0 | 42.69 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `fb90a92c03b11e67` |  |  |
| 2026-11-18T13:27:58+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:27:58+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T13:28:04+00:00 | mutation-changed | 0 | 0.08 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T14:34:26+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T14:37:44+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-18T14:37:53+00:00 | data-load | 1 | 1.22 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `39d84694036a43bc` | Traceback (most recent call last): |  |
| 2026-11-18T14:38:19+00:00 | data-schema-migrate | 0 | 0.39 | `python manage.py migrate --noinput` | `56d728c244009843` |  |  |
| 2026-11-18T14:38:23+00:00 | data-load | 0 | 0.34 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `102e06696c233e34` |  |  |
| 2026-11-18T14:38:27+00:00 | data-export | 1 | 0.28 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out .migration/data/target-export` | `31ae69b6b6c19fa7` |  |  |
| 2026-11-18T14:39:06+00:00 | build-compileall | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T14:39:06+00:00 | build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T14:39:06+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T14:39:06+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T14:39:06+00:00 | idiom-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T14:39:07+00:00 | idiom-ui | 0 | 0.43 | `python .migration/harness/tools/check_ui.py` | `617c55c57b113cf8` |  | gate=ui scope="templates changed since 884612afff7c2c399300b72816e2b6fd75be8054" templates=0 findings=0 |
| 2026-11-18T14:39:16+00:00 | behavior-invariants | 0 | 3.24 | `pytest -q tests/data_migration/test_invariants.py` | `f11959d9a1e9b144` |  |  |
| 2026-11-18T14:39:54+00:00 | regression | 0 | 38.43 | `pytest -q` | `1e13a14851ca8f0b` |  |  |
| 2026-11-18T14:40:38+00:00 | crap-coverage | 0 | 38.07 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `c8a2272086acc985` |  |  |
| 2026-11-18T14:40:38+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T14:40:38+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T14:51:23+00:00 | mutation-changed | 0 | 0.07 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T14:51:42+00:00 | behavior-invariants | 0 | 1.77 | `pytest -q tests/data_migration/test_invariants.py` | `c22487a850faaa14` |  |  |
| 2026-11-18T14:51:42+00:00 | build-compileall | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T14:51:42+00:00 | build-django-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T14:51:42+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T14:51:42+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T14:51:42+00:00 | idiom-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T14:51:43+00:00 | idiom-ui | 0 | 0.4 | `python .migration/harness/tools/check_ui.py` | `617c55c57b113cf8` |  | gate=ui scope="templates changed since 884612afff7c2c399300b72816e2b6fd75be8054" templates=0 findings=0 |
| 2026-11-18T14:52:21+00:00 | regression | 0 | 38.05 | `pytest -q` | `97df75c9613142ff` |  |  |
| 2026-11-18T14:54:07+00:00 | data-reconcile | 1 | 0.06 | `python .migration/harness/tools/data_reconcile.py reconcile --snapshot .migration/data/snapshot --target .migration/data/target-export --mapping .migration/data/mapping.yaml --report .migration/runs/DM-05F/reconciliation.md` | `4fc8ebcf21352d2a` | ::error::location: .migration/data/target-export/location.csv: missing | gate=data-reconcile tables=6 rows=0 mismatched_tables=6 |
