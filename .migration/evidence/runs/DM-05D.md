# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T13:08:47+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:09:17+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-21T13:11:30+00:00 | export-red | 1 | 2.97 | `pytest -q tests/data_migration/test_export.py` | `fa5a0d9acb31be9e` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-21T13:12:08+00:00 | export-green | 0 | 1.43 | `pytest -q tests/data_migration/test_export.py` | `38e13be45293b3a0` |  |  |
| 2026-11-21T13:12:24+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:12:27+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `460bba73f2dafa9b` |  |  |
| 2026-11-21T13:12:34+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-21T13:12:39+00:00 | export-green | 0 | 1.43 | `pytest -q tests/data_migration/test_export.py` | `a558b8376cd28466` |  |  |
| 2026-11-21T13:13:27+00:00 | export-green | 1 | 1.49 | `pytest -q tests/data_migration/test_export.py` | `23c663417b9de9fb` | assert {path.stem for path in output.glob('*.csv')} == { |  |
| 2026-11-21T13:13:36+00:00 | export-green | 0 | 1.45 | `pytest -q tests/data_migration/test_export.py` | `f51873a8b2568bb4` |  |  |
| 2026-11-21T13:13:48+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:13:51+00:00 | build-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T13:14:31+00:00 | behavior | 0 | 37.47 | `pytest -q` | `ba01e4ebbe70024c` |  |  |
| 2026-11-21T13:14:33+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:14:35+00:00 | idiom-ruff-format | 1 | 0.01 | `ruff format --check` | `96354cee5088b4f2` |  |  |
| 2026-11-21T13:14:43+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-21T13:15:24+00:00 | crap-coverage | 0 | 38.3 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `9a7562be233cd86d` |  |  |
| 2026-11-21T13:15:27+00:00 | crap-lizard | 0 | 0.25 | `bash -lc 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:15:29+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `c72029e38f408901` |  | gate=crap max=26.0 threshold=30 over=0 methods=184 |
| 2026-11-21T13:16:38+00:00 | mutation-changed | 1 | 65.04 | `python .migration/harness/tools/afs-mutation` | `e24944342dec08a3` | afs-mutation: FAILED score=0.659 threshold=0.8 killed=54 survived=28 skipped=0 files=2 jobs=2 base=8e1d44445d0f0fc41e10b | gate=mutation score=0.659 threshold=0.8 killed=54 survived=28 files=2 base=8e1d44445d0f0fc41e10b9ada87f80d9f18dd60f |
| 2026-11-21T13:18:00+00:00 | export-hardening | 1 | 1.9 | `pytest -q tests/data_migration/test_export.py` | `b6a5ef8fbfcb75a7` | with pytest.raises(DataExportError) as error: |  |
| 2026-11-21T13:18:10+00:00 | export-hardening | 0 | 1.84 | `pytest -q tests/data_migration/test_export.py` | `d42df7509777e600` |  |  |
| 2026-11-21T13:18:30+00:00 | mutation-changed | 2 | 14.3 | `python .migration/harness/tools/afs-mutation` | `061c6e01777d3653` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=1 files=2 base=8e1d44445d0f0fc41e10b9ada87f80d9f18dd60f |
| 2026-11-21T13:18:53+00:00 | mutation-selector-probe | 0 | 1.13 | `pytest --collect-only -q tests/data_migration/test_export.py::test_export_rejects_invalid_mapping` | `c9e186101df0889c` |  |  |
| 2026-11-21T13:19:53+00:00 | mutation-changed | 2 | 14.16 | `python .migration/harness/tools/afs-mutation` | `c0031d11ba9cd833` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=1 files=2 base=8e1d44445d0f0fc41e10b9ada87f80d9f18dd60f |
