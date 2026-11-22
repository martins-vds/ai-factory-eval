# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T23:43:34+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:45:54+00:00 | export-tests-red | 1 | 2.32 | `pytest -q tests/data_migration/test_export.py` | `dd0f0098aa02026b` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-21T23:46:17+00:00 | export-tests | 0 | 2.01 | `pytest -q tests/data_migration/test_export.py` | `23aad8c8d530c077` |  |  |
| 2026-11-21T23:46:41+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:47:06+00:00 | export-order-test | 0 | 2.16 | `pytest -q tests/data_migration/test_export.py` | `a055b940d481c35c` |  |  |
| 2026-11-21T23:47:09+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `4dc53b3708192cdb` |  |  |
| 2026-11-21T23:47:14+00:00 | format-fix | 0 | 0.01 | `ruff format src/cargotracker/data_migration/exporter.py` | `413a709001976657` |  |  |
| 2026-11-21T23:47:16+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-21T23:47:43+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:48:04+00:00 | build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:48:07+00:00 | build-django-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T23:49:01+00:00 | tests-full | 0 | 50.19 | `pytest -q` | `6a3888dafe9cbe25` |  |  |
| 2026-11-21T23:49:51+00:00 | crap-pytest-coverage | 0 | 47.1 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `a1a6365d7e43507c` |  |  |
| 2026-11-21T23:49:55+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:49:58+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `ce4a3561ad683cc5` |  | gate=crap max=26.0 threshold=30 over=0 methods=185 |
| 2026-11-21T23:50:09+00:00 | mutation-changed | 2 | 7.88 | `python .migration/harness/tools/afs-mutation` | `7d973bc5b5fc83cf` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=2 files=2 base=939fd6e0e29b7dd77ccf0c1267a6ab0d4df62998 |
| 2026-11-21T23:50:48+00:00 | export-tests-portable | 0 | 2.1 | `pytest -q tests/data_migration/test_export.py` | `9a67e93e779f0577` |  |  |
| 2026-11-21T23:50:52+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:50:55+00:00 | idiom-ruff-format | 1 | 0.01 | `ruff format --check` | `d33c8054b4a844cd` |  |  |
| 2026-11-21T23:50:58+00:00 | format-fix | 0 | 0.01 | `ruff format tests/data_migration/test_export.py` | `413a709001976657` |  |  |
| 2026-11-21T23:51:01+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-21T23:52:35+00:00 | mutation-changed | 1 | 91.7 | `python .migration/harness/tools/afs-mutation` | `e6e516baf4d9cf54` | afs-mutation: FAILED score=0.641 threshold=0.8 killed=59 survived=33 skipped=0 files=2 jobs=2 base=939fd6e0e29b7dd77ccf0 | gate=mutation score=0.641 threshold=0.8 killed=59 survived=33 files=2 base=939fd6e0e29b7dd77ccf0c1267a6ab0d4df62998 |
| 2026-11-21T23:53:51+00:00 | export-validation-tests | 1 | 2.26 | `pytest -q tests/data_migration/test_export.py` | `10ad58be02a68bab` | with pytest.raises(CommandError) as error: |  |
| 2026-11-21T23:54:01+00:00 | export-validation-tests | 0 | 2.22 | `pytest -q tests/data_migration/test_export.py` | `6cc80689068fb2b8` |  |  |
| 2026-11-21T23:54:04+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:54:06+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-21T23:54:17+00:00 | mutation-changed | 2 | 7.36 | `python .migration/harness/tools/afs-mutation` | `b3aa8e29f16cf7ec` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=2 files=2 base=939fd6e0e29b7dd77ccf0c1267a6ab0d4df62998 |
| 2026-11-21T23:54:36+00:00 | export-validation-tests | 0 | 2.18 | `pytest -q tests/data_migration/test_export.py` | `b68a6c153f0eabcf` |  |  |
| 2026-11-21T23:54:40+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:54:43+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-21T23:56:19+00:00 | mutation-changed | 1 | 93.55 | `python .migration/harness/tools/afs-mutation` | `58f14a7083d93841` | afs-mutation: FAILED score=0.772 threshold=0.8 killed=71 survived=21 skipped=0 files=2 jobs=2 base=939fd6e0e29b7dd77ccf0 | gate=mutation score=0.772 threshold=0.8 killed=71 survived=21 files=2 base=939fd6e0e29b7dd77ccf0c1267a6ab0d4df62998 |
| 2026-11-21T23:57:05+00:00 | export-command-tests | 1 | 2.53 | `pytest -q tests/data_migration/test_export.py` | `4bd890cd6d578bbe` | self = CommandParser(prog=' export_data_snapshot', usage=None, description='Export mapped target tables as CSV files.',  |  |
| 2026-11-21T23:57:15+00:00 | export-command-tests | 0 | 2.4 | `pytest -q tests/data_migration/test_export.py` | `9232db54307bf226` |  |  |
| 2026-11-21T23:57:18+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:57:20+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-21T23:59:04+00:00 | mutation-changed | 0 | 100.02 | `python .migration/harness/tools/afs-mutation` | `f14cdecddbdb85fe` |  | gate=mutation score=0.815 threshold=0.8 killed=75 survived=17 files=2 base=939fd6e0e29b7dd77ccf0c1267a6ab0d4df62998 |
| 2026-11-22T00:00:14+00:00 | build-compileall | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T00:00:18+00:00 | build-django-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T00:00:22+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T00:00:25+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-22T00:01:17+00:00 | tests-full | 0 | 49.26 | `pytest -q` | `6fbfe42ee0faa2cc` |  |  |
| 2026-11-22T00:02:11+00:00 | crap-pytest-coverage | 0 | 48.83 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `b50696ec6abf43fb` |  |  |
| 2026-11-22T00:02:14+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T00:02:18+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `6fd27a5031ea9911` |  | gate=crap max=26.0 threshold=30 over=0 methods=185 |
| 2026-11-22T00:04:02+00:00 | mutation-changed | 0 | 97.27 | `python .migration/harness/tools/afs-mutation` | `f14cdecddbdb85fe` |  | gate=mutation score=0.815 threshold=0.8 killed=75 survived=17 files=2 base=939fd6e0e29b7dd77ccf0c1267a6ab0d4df62998 |
| 2026-11-22T00:07:54+00:00 | export-tests-final | 0 | 2.35 | `pytest -q tests/data_migration/test_export.py` | `44e8e3588ac7674a` |  |  |
| 2026-11-22T00:07:58+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T00:08:04+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-22T00:09:14+00:00 | tests-full | 0 | 48.75 | `pytest -q` | `d15fbcece2668d04` |  |  |
| 2026-11-22T00:10:04+00:00 | crap-pytest-coverage | 0 | 46.48 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `55b939e1d7e8033b` |  |  |
| 2026-11-22T00:10:07+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T00:10:11+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `6fd27a5031ea9911` |  | gate=crap max=26.0 threshold=30 over=0 methods=185 |
| 2026-11-22T00:11:49+00:00 | mutation-changed | 0 | 94.34 | `python .migration/harness/tools/afs-mutation` | `f14cdecddbdb85fe` |  | gate=mutation score=0.815 threshold=0.8 killed=75 survived=17 files=2 base=939fd6e0e29b7dd77ccf0c1267a6ab0d4df62998 |
