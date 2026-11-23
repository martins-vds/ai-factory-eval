# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T00:43:48+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:44:07+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-23T00:45:48+00:00 | export-tests-red | 1 | 1.91 | `pytest -q tests/data_migration/test_export.py` | `092e91a45747a908` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-23T00:46:16+00:00 | export-tests-green | 1 | 1.71 | `pytest -q tests/data_migration/test_export.py` | `050b23fe833b5cb6` | assert reconciliation.returncode == 0, reconciliation.stdout + reconciliation.stderr |  |
| 2026-11-23T00:46:23+00:00 | export-tests-green | 0 | 1.73 | `pytest -q tests/data_migration/test_export.py` | `0dd8334b9d136db6` |  |  |
| 2026-11-23T00:47:00+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:47:01+00:00 | build-django-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T00:47:01+00:00 | lint-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:47:01+00:00 | format-check | 1 | 0.02 | `ruff format --check` | `10fae0c146ce8319` |  |  |
| 2026-11-23T00:47:09+00:00 | format-check | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-23T00:47:09+00:00 | layers-check | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T00:47:09+00:00 | ui-check | 0 | 0.54 | `python .migration/harness/tools/check_ui.py` | `55cb456d902de042` |  | gate=ui scope="templates changed since 81aa20bcdc6acc38608db76d3f20546cefcfbf4c" templates=0 findings=0 |
| 2026-11-23T00:47:31+00:00 | snapshot-load | 1 | 0.45 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot/ --mapping .migration/data/mapping.yaml` | `39d84694036a43bc` | Traceback (most recent call last): |  |
| 2026-11-23T00:47:41+00:00 | database-migrate | 0 | 0.48 | `python manage.py migrate --noinput` | `56d728c244009843` |  |  |
| 2026-11-23T00:47:41+00:00 | snapshot-load | 0 | 0.43 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot/ --mapping .migration/data/mapping.yaml` | `102e06696c233e34` |  |  |
| 2026-11-23T00:47:42+00:00 | snapshot-export | 0 | 0.4 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out .migration/data/target-export` | `ba754ea10ff616fb` |  |  |
| 2026-11-23T00:47:49+00:00 | snapshot-reconcile | 0 | 0.07 | `python .migration/harness/tools/data_reconcile.py reconcile --snapshot .migration/data/snapshot/ --target .migration/data/target-export/ --mapping .migration/data/mapping.yaml --report /tmp/DM-05D-reconciliation.md` | `0e5f155ede36068f` |  | gate=data-reconcile tables=6 rows=54 mismatched_tables=0 |
| 2026-11-23T00:48:44+00:00 | full-suite | 0 | 44.17 | `pytest -q` | `74c255c9d303ed39` |  |  |
| 2026-11-23T00:49:31+00:00 | crap-coverage | 0 | 43.45 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `da09e24094b91079` |  |  |
| 2026-11-23T00:49:32+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:49:32+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `33bcabeac53eca9f` |  | gate=crap max=26.0 threshold=30 over=0 methods=182 |
| 2026-11-23T00:49:43+00:00 | mutation-changed | 2 | 6.49 | `python .migration/harness/tools/afs-mutation` | `4ea04a4af845fc36` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=2 files=2 base=81aa20bcdc6acc38608db76d3f20546cefcfbf4c |
| 2026-11-23T00:50:09+00:00 | export-tests-green | 0 | 1.76 | `pytest -q tests/data_migration/test_export.py` | `902a1aeb874f13bc` |  |  |
| 2026-11-23T00:50:59+00:00 | mutation-changed | 1 | 47.19 | `python .migration/harness/tools/afs-mutation` | `0c2d705c23db1796` | afs-mutation: FAILED score=0.673 threshold=0.8 killed=37 survived=18 skipped=0 files=2 jobs=2 base=81aa20bcdc6acc38608db | gate=mutation score=0.673 threshold=0.8 killed=37 survived=18 files=2 base=81aa20bcdc6acc38608db76d3f20546cefcfbf4c |
| 2026-11-23T00:51:48+00:00 | export-tests-green | 1 | 1.87 | `pytest -q tests/data_migration/test_export.py` | `4cb8521d022ef618` | with pytest.raises(CommandError) as error: |  |
| 2026-11-23T00:51:57+00:00 | export-tests-green | 0 | 1.83 | `pytest -q tests/data_migration/test_export.py` | `9b238d37dcb2c56a` |  |  |
| 2026-11-23T00:52:47+00:00 | mutation-changed | 0 | 47.32 | `python .migration/harness/tools/afs-mutation` | `d9fed0fdec430a0d` |  | gate=mutation score=0.855 threshold=0.8 killed=47 survived=8 files=2 base=81aa20bcdc6acc38608db76d3f20546cefcfbf4c |
| 2026-11-23T00:53:02+00:00 | build-compile-final | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:53:03+00:00 | build-django-check-final | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T00:53:03+00:00 | lint-ruff-final | 1 | 0.01 | `ruff check` | `0d20d7880021d1e1` | Found 1 error. |  |
| 2026-11-23T00:53:11+00:00 | lint-ruff-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:53:12+00:00 | format-check-final | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-23T00:53:12+00:00 | layers-check-final | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T00:53:12+00:00 | ui-check-final | 0 | 0.55 | `python .migration/harness/tools/check_ui.py` | `55cb456d902de042` |  | gate=ui scope="templates changed since 81aa20bcdc6acc38608db76d3f20546cefcfbf4c" templates=0 findings=0 |
| 2026-11-23T00:53:53+00:00 | full-suite-final | 0 | 37.47 | `pytest -q` | `27ecb36e0c47456b` |  |  |
| 2026-11-23T00:54:35+00:00 | crap-coverage-final | 0 | 38.3 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `fc8d9def398c14a7` |  |  |
| 2026-11-23T00:54:35+00:00 | crap-lizard-final | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:54:35+00:00 | crap-score-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `e91142317d837427` |  | gate=crap max=26.0 threshold=30 over=0 methods=182 |
| 2026-11-23T00:55:27+00:00 | mutation-changed-final | 0 | 47.39 | `python .migration/harness/tools/afs-mutation` | `d9fed0fdec430a0d` |  | gate=mutation score=0.855 threshold=0.8 killed=47 survived=8 files=2 base=81aa20bcdc6acc38608db76d3f20546cefcfbf4c |
