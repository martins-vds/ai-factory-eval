# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T17:47:44+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T17:49:59+00:00 | export-red | 1 | 1.78 | `pytest -q tests/data_migration/test_export.py` | `9daf391cd463ab8d` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T17:50:33+00:00 | export-test | 0 | 1.5 | `pytest -q tests/data_migration/test_export.py` | `7b23e52dabef120c` |  |  |
| 2026-11-15T17:51:02+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T17:51:05+00:00 | build-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T17:51:08+00:00 | idiom-lint | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T17:51:12+00:00 | idiom-format | 1 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `9c413b28d4f16f52` |  |  |
| 2026-11-15T17:51:21+00:00 | idiom-format | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `eee76f865de5a9f2` |  |  |
| 2026-11-15T17:52:02+00:00 | tests | 0 | 36.16 | `pytest -q` | `3735100c13ed8deb` |  |  |
| 2026-11-15T17:52:45+00:00 | crap-coverage | 0 | 36.74 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `ef15d7b60eb740aa` |  |  |
| 2026-11-15T17:52:48+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T17:52:51+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `14d4c6dba54faa49` |  | gate=crap max=26.0 threshold=30 over=0 methods=182 |
| 2026-11-15T17:53:49+00:00 | mutation-changed | 1 | 54.04 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `3d31d74fbde7b014` | afs-mutation: FAILED score=0.745 threshold=0.8 killed=38 survived=13 skipped=0 files=2 jobs=2 base=origin/main | gate=mutation score=0.745 threshold=0.8 killed=38 survived=13 files=2 base=origin/main |
| 2026-11-15T17:54:31+00:00 | export-tests-hardening | 1 | 1.57 | `pytest -q tests/data_migration/test_export.py` | `0b23aba51db97dbd` | with pytest.raises(CommandError) as error: |  |
| 2026-11-15T17:54:42+00:00 | export-tests-hardening | 0 | 1.62 | `pytest -q tests/data_migration/test_export.py` | `16aece7227088486` |  |  |
| 2026-11-15T17:54:58+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T17:55:01+00:00 | build-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T17:55:04+00:00 | idiom-lint | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T17:55:07+00:00 | idiom-format | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `eee76f865de5a9f2` |  |  |
| 2026-11-15T17:55:48+00:00 | tests | 0 | 37.73 | `pytest -q` | `1d1d62dc103b0c26` |  |  |
| 2026-11-15T17:56:27+00:00 | crap-coverage | 0 | 35.38 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `24a58b7e1f98472a` |  |  |
| 2026-11-15T17:56:30+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T17:56:34+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `930b48b91bcde5b4` |  | gate=crap max=26.0 threshold=30 over=0 methods=182 |
| 2026-11-15T17:57:32+00:00 | mutation-changed | 0 | 54.82 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `da593679cfc1036a` |  | gate=mutation score=0.827 threshold=0.8 killed=43 survived=9 files=2 base=origin/main |
| 2026-11-15T17:59:32+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-15T18:00:42+00:00 | data-load | 1 | 0.33 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `39d84694036a43bc` | Traceback (most recent call last): |  |
| 2026-11-15T18:01:00+00:00 | db-migrate | 0 | 0.39 | `python manage.py migrate --noinput` | `56d728c244009843` |  |  |
| 2026-11-15T18:01:04+00:00 | data-load | 0 | 0.34 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `102e06696c233e34` |  |  |
| 2026-11-15T18:01:20+00:00 | data-export | 0 | 0.35 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out /tmp/DM-05D-target-export` | `490617ae37dca389` |  |  |
| 2026-11-15T18:01:26+00:00 | data-reconcile | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py reconcile --snapshot .migration/data/snapshot --target /tmp/DM-05D-target-export --mapping .migration/data/mapping.yaml --report .migration/evidence/data/DM-05D.md` | `0e5f155ede36068f` |  | gate=data-reconcile tables=6 rows=54 mismatched_tables=0 |
