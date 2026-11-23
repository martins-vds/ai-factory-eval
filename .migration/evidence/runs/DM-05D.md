# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T00:43:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:45:29+00:00 | export-red | 1 | 3.06 | `pytest -q tests/data_migration/test_export.py` | `3adc374330483331` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-23T00:46:02+00:00 | export-roundtrip | 0 | 1.85 | `pytest -q tests/data_migration/test_export.py` | `263c94f24c6bf4b6` |  |  |
| 2026-11-23T00:46:09+00:00 | focused-ruff | 1 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `9687f4fe36876830` | Found 1 error. |  |
| 2026-11-23T00:46:13+00:00 | focused-ruff-fix | 0 | 0.01 | `ruff check --fix src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `aac3a0503d8b9505` | Found 1 error (1 fixed, 0 remaining). |  |
| 2026-11-23T00:46:29+00:00 | focused-ruff | 1 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `25c7cc9cdc176530` | Found 1 error. |  |
| 2026-11-23T00:46:31+00:00 | export-focused-tests | 0 | 1.98 | `pytest -q tests/data_migration/test_export.py` | `88926c1833d969b0` |  |  |
| 2026-11-23T00:46:34+00:00 | focused-ruff-fix | 0 | 0.01 | `ruff check --fix src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `aac3a0503d8b9505` | Found 1 error (1 fixed, 0 remaining). |  |
| 2026-11-23T00:46:40+00:00 | focused-ruff | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:46:40+00:00 | focused-format | 1 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `17df3cf70f917d74` |  |  |
| 2026-11-23T00:46:42+00:00 | export-focused-tests-final | 0 | 2.08 | `pytest -q tests/data_migration/test_export.py` | `8f6abe38f9b13362` |  |  |
| 2026-11-23T00:46:45+00:00 | focused-format-fix | 0 | 0.01 | `ruff format src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `44b7183e1f210a48` |  |  |
| 2026-11-23T00:46:56+00:00 | focused-ruff-final | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:46:57+00:00 | focused-format-final | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `eee76f865de5a9f2` |  |  |
| 2026-11-23T00:46:58+00:00 | export-focused-tests-final | 0 | 2.07 | `pytest -q tests/data_migration/test_export.py` | `7dae9c85117603cd` |  |  |
| 2026-11-23T00:47:31+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot/` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-23T00:47:40+00:00 | snapshot-load | 1 | 0.44 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot/ --mapping .migration/data/mapping.yaml` | `39d84694036a43bc` | Traceback (most recent call last): |  |
| 2026-11-23T00:47:52+00:00 | database-migration-plan | 0 | 0.42 | `python manage.py migrate --plan` | `841635093d753223` |  |  |
| 2026-11-23T00:47:56+00:00 | database-migrate | 0 | 0.51 | `python manage.py migrate --noinput` | `56d728c244009843` |  |  |
| 2026-11-23T00:48:00+00:00 | snapshot-load | 0 | 0.43 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot/ --mapping .migration/data/mapping.yaml` | `102e06696c233e34` |  |  |
| 2026-11-23T00:48:03+00:00 | snapshot-export | 0 | 0.42 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out .migration/data/target-export/` | `ba754ea10ff616fb` |  |  |
| 2026-11-23T00:48:25+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:48:27+00:00 | build-check | 0 | 0.39 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T00:48:30+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:48:32+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-23T00:48:34+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T00:48:38+00:00 | idiom-ui | 0 | 0.73 | `python .migration/harness/tools/check_ui.py` | `f12fd2d3086e0571` |  | gate=ui scope="templates changed since af7b0f50a4466466d767a8b3fe238a5cb3c2ef8f" templates=0 findings=0 |
| 2026-11-23T00:49:39+00:00 | behavior | 0 | 58.8 | `pytest -q` | `126fa1e53d74a221` |  |  |
| 2026-11-23T00:50:33+00:00 | crap-coverage | 0 | 50.33 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `798b3a2814fdacec` |  |  |
| 2026-11-23T00:50:36+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:50:38+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `f2b725d165841675` |  | gate=crap max=26.0 threshold=30 over=0 methods=181 |
| 2026-11-23T00:51:31+00:00 | mutation-changed | 1 | 50.35 | `python .migration/harness/tools/afs-mutation` | `5e2f94a2e232974a` | afs-mutation: FAILED score=0.679 threshold=0.8 killed=36 survived=17 skipped=0 files=2 jobs=2 base=af7b0f50a4466466d767a | gate=mutation score=0.679 threshold=0.8 killed=36 survived=17 files=2 base=af7b0f50a4466466d767a8b3fe238a5cb3c2ef8f |
| 2026-11-23T00:52:06+00:00 | export-mutation-tests | 0 | 2.04 | `pytest -q tests/data_migration/test_export.py` | `97a9c113392c5109` |  |  |
| 2026-11-23T00:52:10+00:00 | focused-style-after-mutation-tests | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:52:10+00:00 | focused-format-after-mutation-tests | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `eee76f865de5a9f2` |  |  |
| 2026-11-23T00:53:10+00:00 | mutation-changed-final | 0 | 49.53 | `python .migration/harness/tools/afs-mutation` | `114f534c636e4bc5` |  | gate=mutation score=0.868 threshold=0.8 killed=46 survived=7 files=2 base=af7b0f50a4466466d767a8b3fe238a5cb3c2ef8f |
| 2026-11-23T00:54:04+00:00 | regression-final | 0 | 47.03 | `pytest -q` | `f662ce14da4c3215` |  |  |
| 2026-11-23T00:54:54+00:00 | export-rfc4180-test | 0 | 2.03 | `pytest -q tests/data_migration/test_export.py` | `97a9c113392c5109` |  |  |
| 2026-11-23T00:54:58+00:00 | style-rfc4180 | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:54:58+00:00 | format-rfc4180 | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `eee76f865de5a9f2` |  |  |
| 2026-11-23T00:55:18+00:00 | final-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:55:21+00:00 | final-build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T00:55:24+00:00 | final-idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:55:26+00:00 | final-idiom-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-23T00:55:29+00:00 | final-idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T00:55:33+00:00 | final-idiom-ui | 0 | 0.72 | `python .migration/harness/tools/check_ui.py` | `f12fd2d3086e0571` |  | gate=ui scope="templates changed since af7b0f50a4466466d767a8b3fe238a5cb3c2ef8f" templates=0 findings=0 |
| 2026-11-23T00:55:38+00:00 | final-behavior | 0 | 2.03 | `pytest -q tests/data_migration/test_export.py` | `7df9fce5e0db6a25` |  |  |
| 2026-11-23T00:56:38+00:00 | final-regression | 0 | 57.35 | `pytest -q` | `4e4d7b13128dac15` |  |  |
| 2026-11-23T00:57:32+00:00 | final-crap-coverage | 0 | 50.5 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `8d49afb14c9e00cd` |  |  |
| 2026-11-23T00:57:36+00:00 | final-crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:57:39+00:00 | final-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `f2b725d165841675` |  | gate=crap max=26.0 threshold=30 over=0 methods=181 |
| 2026-11-23T00:58:31+00:00 | final-mutation-changed | 0 | 49.38 | `python .migration/harness/tools/afs-mutation` | `3ebf34ebdb3c764d` |  | gate=mutation score=0.865 threshold=0.8 killed=45 survived=7 files=2 base=af7b0f50a4466466d767a8b3fe238a5cb3c2ef8f |
| 2026-11-23T01:01:07+00:00 | snapshot-export-final | 0 | 0.4 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out .migration/data/target-export/` | `ba754ea10ff616fb` |  |  |
| 2026-11-23T01:05:57+00:00 | finish-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:06:00+00:00 | finish-build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T01:06:06+00:00 | finish-behavior | 0 | 2.04 | `pytest -q tests/data_migration/test_export.py` | `97a9c113392c5109` |  |  |
| 2026-11-23T01:06:09+00:00 | finish-idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T01:06:12+00:00 | finish-idiom-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-23T01:06:15+00:00 | finish-idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T01:06:19+00:00 | finish-idiom-ui | 0 | 0.74 | `python .migration/harness/tools/check_ui.py` | `f12fd2d3086e0571` |  | gate=ui scope="templates changed since af7b0f50a4466466d767a8b3fe238a5cb3c2ef8f" templates=0 findings=0 |
| 2026-11-23T01:07:13+00:00 | finish-crap-coverage | 0 | 50.85 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `8e3ff92279398890` |  |  |
| 2026-11-23T01:07:17+00:00 | finish-crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:07:20+00:00 | finish-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `f2b725d165841675` |  | gate=crap max=26.0 threshold=30 over=0 methods=181 |
| 2026-11-23T01:08:11+00:00 | finish-regression | 0 | 48.24 | `pytest -q` | `3809df8a2e8dd917` |  |  |
| 2026-11-23T01:09:06+00:00 | finish-mutation-changed | 0 | 51.36 | `python .migration/harness/tools/afs-mutation` | `3ebf34ebdb3c764d` |  | gate=mutation score=0.865 threshold=0.8 killed=45 survived=7 files=2 base=af7b0f50a4466466d767a8b3fe238a5cb3c2ef8f |
