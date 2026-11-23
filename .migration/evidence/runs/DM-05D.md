# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T00:43:59+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:44:37+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-23T00:46:05+00:00 | export-tests-red | 1 | 3.91 | `pytest -q tests/data_migration/test_export.py` | `82a3261b38114d1e` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-23T00:46:35+00:00 | export-tests-green | 0 | 2.08 | `pytest -q tests/data_migration/test_export.py` | `a0e97fe67f271e48` |  |  |
| 2026-11-23T00:47:00+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:47:03+00:00 | build-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T00:47:05+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:47:08+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-23T00:47:11+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T00:47:14+00:00 | idiom-ui | 0 | 0.71 | `python .migration/harness/tools/check_ui.py` | `a8721e4fb03ea761` |  | gate=ui scope="templates changed since f415794e3aff44382d65a23c7841c416c0678532" templates=0 findings=0 |
| 2026-11-23T00:48:08+00:00 | regression | 0 | 51.18 | `pytest -q` | `76884b71587bd1fa` |  |  |
| 2026-11-23T00:48:59+00:00 | crap-coverage | 0 | 47.21 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `02f0fb80733073e1` |  |  |
| 2026-11-23T00:49:03+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:49:07+00:00 | crap-check | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `dff7f257d794117d` |  | gate=crap max=26.0 threshold=30 over=0 methods=185 |
| 2026-11-23T00:49:18+00:00 | mutation-changed | 2 | 7.96 | `python .migration/harness/tools/afs-mutation` | `b29f41e7ac968baa` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=2 files=2 base=f415794e3aff44382d65a23c7841c416c0678532 |
| 2026-11-23T00:49:48+00:00 | export-tests-green-2 | 0 | 2.04 | `pytest -q tests/data_migration/test_export.py` | `23aad8c8d530c077` |  |  |
| 2026-11-23T00:51:45+00:00 | mutation-changed | 1 | 88.03 | `python .migration/harness/tools/afs-mutation` | `356c7b0d3d512314` | afs-mutation: FAILED score=0.616 threshold=0.8 killed=53 survived=33 skipped=0 files=2 jobs=2 base=f415794e3aff44382d65a | gate=mutation score=0.616 threshold=0.8 killed=53 survived=33 files=2 base=f415794e3aff44382d65a23c7841c416c0678532 |
| 2026-11-23T00:52:48+00:00 | export-tests-mutation-coverage | 1 | 2.32 | `pytest -q tests/data_migration/test_export.py` | `433c01f2f011e870` | assert {path.name for path in output.glob('*.csv')} == set(expected_tables) |  |
| 2026-11-23T00:53:02+00:00 | export-tests-mutation-coverage-2 | 0 | 2.25 | `pytest -q tests/data_migration/test_export.py` | `5b2c817138d1d2cf` |  |  |
| 2026-11-23T00:53:14+00:00 | export-tests-final | 0 | 2.22 | `pytest -q tests/data_migration/test_export.py` | `9c28f57c4fad4b6d` |  |  |
| 2026-11-23T00:53:39+00:00 | mutation-changed | 2 | 7.73 | `python .migration/harness/tools/afs-mutation` | `4bf8c5f3dc0d3854` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=2 files=2 base=f415794e3aff44382d65a23c7841c416c0678532 |
| 2026-11-23T00:53:54+00:00 | export-tests-mutation-discovery | 0 | 2.22 | `pytest -q tests/data_migration/test_export.py` | `8b095f83baeb8b1c` |  |  |
| 2026-11-23T00:55:40+00:00 | mutation-changed | 0 | 88.04 | `python .migration/harness/tools/afs-mutation` | `b794aaf09c88c7f0` |  | gate=mutation score=0.930 threshold=0.8 killed=80 survived=6 files=2 base=f415794e3aff44382d65a23c7841c416c0678532 |
| 2026-11-23T00:56:18+00:00 | export-tests-survivor-cases | 0 | 2.23 | `pytest -q tests/data_migration/test_export.py` | `2b8f17307e76a363` |  |  |
