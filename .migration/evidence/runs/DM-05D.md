# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T23:44:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T23:47:44+00:00 | tdd-roundtrip-red | 1 | 1.91 | `pytest -q tests/data_migration/test_export.py` | `21ae232261d0cd1c` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T23:48:19+00:00 | tdd-roundtrip-green | 0 | 1.64 | `pytest -q tests/data_migration/test_export.py` | `a2ff0172c1450afa` |  |  |
| 2026-11-15T23:48:59+00:00 | focused-export-tests | 0 | 1.87 | `pytest -q tests/data_migration/test_export.py` | `7d4c2db06b269aea` |  |  |
| 2026-11-15T23:49:37+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T23:49:40+00:00 | build-django-check | 0 | 0.34 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T23:50:26+00:00 | behavior | 0 | 42.84 | `pytest -q` | `eb81c6310c3278ad` |  |  |
| 2026-11-15T23:50:31+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T23:50:34+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `cdf300a57506ecc8` |  |  |
| 2026-11-15T23:50:45+00:00 | idiom-changed-format | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `eee76f865de5a9f2` |  |  |
| 2026-11-15T23:51:31+00:00 | crap-coverage | 0 | 42.78 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `63407970edf1c5da` |  |  |
| 2026-11-15T23:51:35+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T23:51:39+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `927eaf929a841343` |  | gate=crap max=26.0 threshold=30 over=0 methods=181 |
| 2026-11-15T23:51:54+00:00 | mutation-changed | 2 | 6.79 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `172d3833ddca5571` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=2 files=2 base=origin/main |
| 2026-11-15T23:53:26+00:00 | focused-export-tests-rerun | 0 | 1.85 | `pytest -q tests/data_migration/test_export.py` | `7148faa3cea19749` |  |  |
| 2026-11-15T23:54:54+00:00 | mutation-changed-rerun | 1 | 68.77 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `4afd3bb7208cb5c5` | afs-mutation: FAILED score=0.660 threshold=0.8 killed=35 survived=18 skipped=0 files=2 jobs=2 base=origin/main | gate=mutation score=0.660 threshold=0.8 killed=35 survived=18 files=2 base=origin/main |
| 2026-11-15T23:56:05+00:00 | focused-export-mutant-tests | 0 | 1.83 | `pytest -q tests/data_migration/test_export.py` | `d1521d54e789cdf1` |  |  |
| 2026-11-15T23:57:11+00:00 | mutation-changed-final | 0 | 44.79 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `72141937f9925073` |  | gate=mutation score=0.849 threshold=0.8 killed=45 survived=8 files=2 base=origin/main |
