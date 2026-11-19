# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T21:39:22+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:42:24+00:00 | export-red | 1 | 2.72 | `pytest -q tests/data_migration/test_export.py` | `7ea949325fa35710` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-19T21:43:02+00:00 | export-green | 0 | 1.57 | `pytest -q tests/data_migration/test_export.py` | `a41ffd9d3e4191f8` |  |  |
| 2026-11-19T21:43:35+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:43:35+00:00 | build-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T21:44:17+00:00 | tests | 0 | 38.47 | `pytest -q` | `860d5a5463f3de5c` |  |  |
| 2026-11-19T21:44:21+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:44:21+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-19T21:45:04+00:00 | crap-coverage | 0 | 36.21 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `88e7905d7ffe04ae` |  |  |
| 2026-11-19T21:45:04+00:00 | crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:45:05+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `b2e05a5cce1f9a0c` |  | gate=crap max=26.0 threshold=30 over=0 methods=184 |
| 2026-11-19T21:45:14+00:00 | mutation-changed | 2 | 6.18 | `python .migration/harness/tools/afs-mutation` | `2d0cd2123d807902` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=2 files=2 base=f588d5360f7175491af1ab3d9688571ea0fd7d2f |
| 2026-11-19T21:45:59+00:00 | export-without-harness | 0 | 1.6 | `pytest -q tests/data_migration/test_export.py` | `38c3fe21dfbb0ecf` |  |  |
| 2026-11-19T21:47:05+00:00 | mutation-changed | 1 | 62.0 | `python .migration/harness/tools/afs-mutation` | `05511c637fd79c95` | afs-mutation: FAILED score=0.628 threshold=0.8 killed=49 survived=29 skipped=0 files=2 jobs=2 base=f588d5360f7175491af1a | gate=mutation score=0.628 threshold=0.8 killed=49 survived=29 files=2 base=f588d5360f7175491af1ab3d9688571ea0fd7d2f |
| 2026-11-19T21:47:55+00:00 | export-validation-tests | 0 | 1.61 | `pytest -q tests/data_migration/test_export.py` | `a8c5082c8be5790b` |  |  |
| 2026-11-19T21:49:00+00:00 | mutation-changed | 1 | 60.8 | `python .migration/harness/tools/afs-mutation` | `ba854594d09ffbe3` | afs-mutation: FAILED score=0.795 threshold=0.8 killed=62 survived=16 skipped=0 files=2 jobs=2 base=f588d5360f7175491af1a | gate=mutation score=0.795 threshold=0.8 killed=62 survived=16 files=2 base=f588d5360f7175491af1ab3d9688571ea0fd7d2f |
| 2026-11-19T21:49:15+00:00 | export-error-message | 0 | 1.65 | `pytest -q tests/data_migration/test_export.py` | `81a53404aa582b37` |  |  |
| 2026-11-19T21:50:18+00:00 | mutation-changed | 0 | 60.19 | `python .migration/harness/tools/afs-mutation` | `8d7567747adc4f7a` |  | gate=mutation score=0.808 threshold=0.8 killed=63 survived=15 files=2 base=f588d5360f7175491af1ab3d9688571ea0fd7d2f |
| 2026-11-19T21:51:41+00:00 | export-assertions | 1 | 1.65 | `pytest -q tests/data_migration/test_export.py` | `cc6b38ef9bd65000` | assert exit_error.value.code == 0 |  |
| 2026-11-19T21:51:52+00:00 | export-assertions | 0 | 1.6 | `pytest -q tests/data_migration/test_export.py` | `ddad644482ee8aa5` |  |  |
| 2026-11-19T21:52:02+00:00 | mutation-changed | 2 | 5.62 | `python .migration/harness/tools/afs-mutation` | `01c3455e9039e4ef` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=2 files=2 base=f588d5360f7175491af1ab3d9688571ea0fd7d2f |
| 2026-11-19T21:52:24+00:00 | export-assertions | 0 | 1.61 | `pytest -q tests/data_migration/test_export.py` | `5e40130a02f243a9` |  |  |
| 2026-11-19T21:53:28+00:00 | mutation-changed | 0 | 58.68 | `python .migration/harness/tools/afs-mutation` | `a4f74addbd8caea3` |  | gate=mutation score=0.936 threshold=0.8 killed=73 survived=5 files=2 base=f588d5360f7175491af1ab3d9688571ea0fd7d2f |
| 2026-11-19T21:53:37+00:00 | export-help | 0 | 0.29 | `python manage.py export_data_snapshot --help` | `fbaaf46fcd379041` | [--pythonpath PYTHONPATH] [--traceback] |  |
| 2026-11-19T21:53:49+00:00 | export-help-assertion | 0 | 1.59 | `pytest -q tests/data_migration/test_export.py` | `256942bcef2fa1c0` |  |  |
| 2026-11-19T21:54:53+00:00 | mutation-changed | 0 | 60.69 | `python .migration/harness/tools/afs-mutation` | `85a51774a7cdfe9f` |  | gate=mutation score=0.949 threshold=0.8 killed=74 survived=4 files=2 base=f588d5360f7175491af1ab3d9688571ea0fd7d2f |
| 2026-11-19T21:55:32+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-19T21:55:37+00:00 | data-load | 1 | 0.38 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `39d84694036a43bc` | Traceback (most recent call last): |  |
| 2026-11-19T21:55:50+00:00 | database-migrate | 0 | 0.39 | `python manage.py migrate --noinput` | `56d728c244009843` |  |  |
| 2026-11-19T21:55:51+00:00 | data-load | 0 | 0.34 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `102e06696c233e34` |  |  |
| 2026-11-19T21:55:51+00:00 | data-export | 0 | 0.33 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out .migration/data/target-export` | `ba754ea10ff616fb` |  |  |
| 2026-11-19T21:55:51+00:00 | data-reconcile | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py reconcile --snapshot .migration/data/snapshot --target .migration/data/target-export --mapping .migration/data/mapping.yaml --report .migration/runs/DM-05D/reconciliation.md` | `0e5f155ede36068f` |  | gate=data-reconcile tables=6 rows=54 mismatched_tables=0 |
| 2026-11-19T21:56:44+00:00 | tests | 0 | 35.54 | `pytest -q` | `70982aeb7187f9f0` |  |  |
| 2026-11-19T21:56:45+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:56:45+00:00 | build-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T21:56:45+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:56:45+00:00 | idiom-format | 1 | 0.01 | `ruff format --check` | `c17d7b9b634b9df9` | -     assert str(error.value).startswith( |  |
| 2026-11-19T21:56:58+00:00 | export-final | 0 | 1.58 | `pytest -q tests/data_migration/test_export.py` | `ab52ad72e1fde7ba` |  |  |
| 2026-11-19T21:56:58+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-19T21:56:58+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:57:48+00:00 | crap-coverage | 0 | 34.94 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `04e10972dd4cecd0` |  |  |
| 2026-11-19T21:57:49+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:57:49+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `eb7f749017d02009` |  | gate=crap max=26.0 threshold=30 over=0 methods=184 |
