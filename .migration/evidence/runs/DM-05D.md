# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T20:35:38+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:38:42+00:00 | export-red | 1 | 1.39 | `python -m pytest -q tests/data_migration/test_export.py` | `d999d3049b3b3741` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-16T20:39:16+00:00 | export-green | 1 | 1.08 | `python -m pytest -q tests/data_migration/test_export.py` | `09894a73a987a570` | >       assert _read_csv(out / 'location.csv') == [ |  |
| 2026-11-16T20:39:28+00:00 | export-green | 0 | 1.05 | `python -m pytest -q tests/data_migration/test_export.py` | `27d1253d12cbb0a1` |  |  |
| 2026-11-16T20:40:14+00:00 | export-green | 0 | 1.07 | `python -m pytest -q tests/data_migration/test_export.py` | `81efd79c27213e56` |  |  |
| 2026-11-16T20:41:02+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:41:05+00:00 | build-check | 0 | 0.21 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T20:41:09+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T20:41:13+00:00 | idiom-format | 1 | 0.01 | `ruff format --check` | `375da3edc53b5373` |  |  |
| 2026-11-16T20:41:22+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `c7a0bcb17dd5241a` |  |  |
| 2026-11-16T20:41:25+00:00 | export-green | 0 | 1.06 | `python -m pytest -q tests/data_migration/test_export.py` | `d8a9947dcb784387` |  |  |
| 2026-11-16T20:41:31+00:00 | export-cli | 1 | 0.24 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out /tmp/dm05d-target-export` | `202a9a74c258d904` | Traceback (most recent call last): |  |
| 2026-11-16T20:41:42+00:00 | cli-migrate | 0 | 0.28 | `python manage.py migrate --noinput` | `56d728c244009843` |  |  |
| 2026-11-16T20:41:46+00:00 | export-cli | 0 | 0.24 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out /tmp/dm05d-target-export` | `459d7b68e57947ec` |  |  |
| 2026-11-16T20:42:14+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T20:42:18+00:00 | snapshot-load | 0 | 0.25 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `102e06696c233e34` |  |  |
| 2026-11-16T20:42:22+00:00 | snapshot-export | 0 | 0.24 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out /tmp/dm05d-target-export` | `ba754ea10ff616fb` |  |  |
| 2026-11-16T20:42:27+00:00 | snapshot-reconcile | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py reconcile --snapshot .migration/data/snapshot --target /tmp/dm05d-target-export --mapping .migration/data/mapping.yaml --report /tmp/dm05d-reconciliation.md` | `0e5f155ede36068f` |  | gate=data-reconcile tables=6 rows=54 mismatched_tables=0 |
| 2026-11-16T20:43:09+00:00 | regression | 0 | 30.56 | `pytest -q` | `9f8e05327f980477` |  |  |
| 2026-11-16T20:43:40+00:00 | crap-coverage | 0 | 26.3 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `a57516a1e10618cf` |  |  |
| 2026-11-16T20:43:42+00:00 | crap-lizard | 0 | 0.08 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:43:47+00:00 | crap-report | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `eff9c32b362fbe83` |  | gate=crap max=26.0 threshold=30 over=0 methods=184 |
| 2026-11-16T20:44:40+00:00 | mutation-changed | 1 | 48.27 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `3d73ad9a771263bd` | afs-mutation: FAILED score=0.628 threshold=0.8 killed=49 survived=29 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.628 threshold=0.8 killed=49 survived=29 files=1 base=origin/main |
| 2026-11-16T20:46:22+00:00 | export-tests-expanded | 1 | 1.29 | `python -m pytest -q tests/data_migration/test_export.py` | `9cbdb5530c5b18eb` | >       assert command_output.getvalue().strip() == 'Exported 54 rows across 6 mapped tables.' |  |
| 2026-11-16T20:46:47+00:00 | export-tests-expanded | 1 | 1.25 | `python -m pytest -q tests/data_migration/test_export.py` | `db0685ac3261e37c` | error = 'no target column' |  |
| 2026-11-16T20:46:58+00:00 | export-tests-expanded | 0 | 1.22 | `python -m pytest -q tests/data_migration/test_export.py` | `4f9388d0687553c9` |  |  |
| 2026-11-16T20:47:04+00:00 | restore-db | 0 | 0.23 | `python manage.py flush --noinput` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:47:58+00:00 | mutation-changed | 0 | 49.5 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `1925f9acb951f0b5` |  | gate=mutation score=0.813 threshold=0.8 killed=61 survived=14 files=1 base=origin/main |
