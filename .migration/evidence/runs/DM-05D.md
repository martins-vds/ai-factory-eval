# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-20T00:34:38+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:38:07+00:00 | export-test-red | 1 | 2.81 | `pytest -q tests/data_migration/test_export.py` | `4fa8ca0dd56fe97b` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-20T00:39:12+00:00 | export-test-green | 1 | 1.54 | `pytest -q tests/data_migration/test_export.py` | `ab5daeeac359a746` | assert {path.stem for path in output.glob('*.csv')} == { |  |
| 2026-11-20T00:39:45+00:00 | export-test-green | 0 | 1.54 | `pytest -q tests/data_migration/test_export.py` | `a41ffd9d3e4191f8` |  |  |
| 2026-11-20T00:40:05+00:00 | export-ruff | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:40:10+00:00 | export-format | 1 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `f702f15fe10ccbf9` | 43 \|         assert data[0] == list(spec['columns']) |  |
| 2026-11-20T00:40:17+00:00 | export-format-fix | 0 | 0.01 | `ruff format src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `292ab567521d3084` |  |  |
| 2026-11-20T00:40:27+00:00 | export-test-green | 0 | 1.51 | `pytest -q tests/data_migration/test_export.py` | `76a0f2a0e9a6c1a5` |  |  |
| 2026-11-20T00:40:30+00:00 | export-format-check | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `eee76f865de5a9f2` |  |  |
| 2026-11-20T00:41:21+00:00 | export-test-green | 0 | 1.52 | `pytest -q tests/data_migration/test_export.py` | `76a0f2a0e9a6c1a5` |  |  |
| 2026-11-20T00:41:44+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-20T00:41:52+00:00 | export-ruff | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:41:57+00:00 | export-format-check | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `eee76f865de5a9f2` |  |  |
| 2026-11-20T00:42:30+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:42:35+00:00 | build-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T00:43:16+00:00 | behavior | 0 | 37.09 | `pytest -q` | `4877bf71573d5d73` |  |  |
| 2026-11-20T00:43:20+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:43:23+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-20T00:44:08+00:00 | crap-coverage | 0 | 34.84 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `4538924aba31eab8` |  |  |
| 2026-11-20T00:44:20+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:44:23+00:00 | crap-check | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `96e71c291c816251` |  | gate=crap max=26.0 threshold=30 over=0 methods=185 |
| 2026-11-20T00:46:01+00:00 | mutation-changed | 1 | 94.35 | `python .migration/harness/tools/afs-mutation` | `c7cfa69ad2e16f34` | afs-mutation: FAILED score=0.632 threshold=0.8 killed=48 survived=28 skipped=0 files=2 jobs=2 base=bbd42f104df4a113ac650 | gate=mutation score=0.632 threshold=0.8 killed=48 survived=28 files=2 base=bbd42f104df4a113ac65034b433328055fd8295b |
| 2026-11-20T00:47:26+00:00 | export-test-strengthened | 0 | 1.61 | `pytest -q tests/data_migration/test_export.py` | `885a76b01320969b` |  |  |
| 2026-11-20T00:48:58+00:00 | mutation-changed | 1 | 87.91 | `python .migration/harness/tools/afs-mutation` | `288e8f76baa34cb4` | afs-mutation: FAILED score=0.789 threshold=0.8 killed=60 survived=16 skipped=0 files=2 jobs=2 base=bbd42f104df4a113ac650 | gate=mutation score=0.789 threshold=0.8 killed=60 survived=16 files=2 base=bbd42f104df4a113ac65034b433328055fd8295b |
| 2026-11-20T00:49:34+00:00 | export-test-timezone | 1 | 1.6 | `pytest -q tests/data_migration/test_export.py` | `dfafb35d771d7633` | assert stdout.getvalue().strip() == 'Exported 7 rows across 6 mapped tables.' |  |
| 2026-11-20T00:50:29+00:00 | export-test-naive | 0 | 1.6 | `pytest -q tests/data_migration/test_export.py` | `ce4950deb2f2a171` |  |  |
| 2026-11-20T00:51:58+00:00 | mutation-changed | 0 | 83.48 | `python .migration/harness/tools/afs-mutation` | `6e5ddc172df55315` |  | gate=mutation score=0.803 threshold=0.8 killed=61 survived=15 files=2 base=bbd42f104df4a113ac65034b433328055fd8295b |
| 2026-11-20T00:52:51+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:52:53+00:00 | build-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T00:53:33+00:00 | behavior | 0 | 37.08 | `pytest -q` | `9ff6db806135abc5` |  |  |
| 2026-11-20T00:53:37+00:00 | idiom-ruff | 1 | 0.01 | `ruff check` | `1f6b3855b786ad68` | Found 1 error. |  |
| 2026-11-20T00:53:43+00:00 | idiom-ruff-fix | 0 | 0.01 | `ruff check --fix tests/data_migration/test_export.py` | `aac3a0503d8b9505` | Found 1 error (1 fixed, 0 remaining). |  |
| 2026-11-20T00:53:46+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:53:49+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-20T00:54:15+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:54:21+00:00 | build-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T00:55:00+00:00 | behavior | 0 | 35.69 | `pytest -q` | `894777fb7dd9e854` |  |  |
| 2026-11-20T00:55:03+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:55:06+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-20T00:55:45+00:00 | crap-coverage | 0 | 35.39 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `a76268028b9c49c1` |  |  |
| 2026-11-20T00:55:50+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:55:54+00:00 | crap-check | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `37484b3765632376` |  | gate=crap max=26.0 threshold=30 over=0 methods=185 |
| 2026-11-20T00:57:21+00:00 | mutation-changed | 0 | 83.83 | `python .migration/harness/tools/afs-mutation` | `6e5ddc172df55315` |  | gate=mutation score=0.803 threshold=0.8 killed=61 survived=15 files=2 base=bbd42f104df4a113ac65034b433328055fd8295b |
| 2026-11-20T01:00:28+00:00 | export-test-review-fix | 0 | 1.58 | `pytest -q tests/data_migration/test_export.py` | `ce4950deb2f2a171` |  |  |
| 2026-11-20T01:00:31+00:00 | export-ruff | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T01:00:35+00:00 | export-format | 1 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `9cef11674c54885a` | -     assert { |  |
| 2026-11-20T01:00:40+00:00 | export-format-fix | 0 | 0.01 | `ruff format tests/data_migration/test_export.py` | `413a709001976657` |  |  |
| 2026-11-20T01:00:46+00:00 | export-test-review-fix | 0 | 1.58 | `pytest -q tests/data_migration/test_export.py` | `08a1ba19c890ef94` |  |  |
| 2026-11-20T01:01:14+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T01:01:19+00:00 | build-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T01:02:01+00:00 | behavior | 0 | 35.97 | `pytest -q` | `cfb68e1eaaceb541` |  |  |
| 2026-11-20T01:02:06+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T01:02:11+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-20T01:02:50+00:00 | crap-coverage | 0 | 34.25 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `f33aea2941b76d5b` |  |  |
| 2026-11-20T01:02:56+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T01:03:03+00:00 | crap-check | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `37484b3765632376` |  | gate=crap max=26.0 threshold=30 over=0 methods=185 |
| 2026-11-20T01:04:31+00:00 | mutation-changed | 0 | 83.19 | `python .migration/harness/tools/afs-mutation` | `6e5ddc172df55315` |  | gate=mutation score=0.803 threshold=0.8 killed=61 survived=15 files=2 base=bbd42f104df4a113ac65034b433328055fd8295b |
