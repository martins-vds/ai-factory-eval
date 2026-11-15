# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T02:39:37+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T02:42:27+00:00 | export-red | 1 | 3.25 | `pytest -q tests/data_migration/test_export.py` | `c1833eae99e0edee` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T02:43:18+00:00 | export-tests | 0 | 1.02 | `pytest -q tests/data_migration/test_export.py` | `c45b5c446e3c4c9b` |  |  |
| 2026-11-15T02:43:40+00:00 | data-migration-tests | 0 | 3.11 | `pytest -q tests/data_migration/` | `1b92966aec6aadb0` |  |  |
| 2026-11-15T02:44:06+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T02:44:09+00:00 | build-check | 0 | 0.22 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T02:44:13+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T02:44:17+00:00 | idiom-ruff-format | 1 | 0.01 | `ruff format --check` | `0887781845c98c00` | 29 \|             assert reader.fieldnames == list(spec['columns']) |  |
| 2026-11-15T02:44:25+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `c7a0bcb17dd5241a` |  |  |
| 2026-11-15T02:44:57+00:00 | behavior | 0 | 28.37 | `pytest -q` | `a35b409af22d91b9` |  |  |
| 2026-11-15T02:45:28+00:00 | crap-coverage | 0 | 27.57 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `88901f6435ae1b87` |  |  |
| 2026-11-15T02:45:32+00:00 | crap-lizard | 0 | 0.08 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T02:45:35+00:00 | crap-report | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `3a79e0714628f7f1` |  | gate=crap max=28.5 threshold=30 over=0 methods=184 |
| 2026-11-15T03:19:32+00:00 | mutation-changed | 2 | 2032.87 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `624adf8c843c44d1` | afs-mutation: mutmut failed on src/cargotracker/data_migration/loader.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=1 files=77 base=origin/main |
| 2026-11-15T03:20:48+00:00 | data-migration-tests | 1 | 3.19 | `pytest -q tests/data_migration/` | `7b28e24538f8f381` | >               assert reader.fieldnames == list(spec['columns']) |  |
| 2026-11-15T03:21:00+00:00 | data-migration-tests | 0 | 3.06 | `pytest -q tests/data_migration/` | `3713dc06cc2a0264` |  |  |
| 2026-11-15T03:21:09+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T03:21:13+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `c7a0bcb17dd5241a` |  |  |
| 2026-11-15T03:21:47+00:00 | regression | 0 | 29.03 | `pytest -q` | `42026e39eaf3abda` |  |  |
| 2026-11-15T03:22:19+00:00 | crap-coverage | 0 | 28.9 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `09c1d9f8b657c1d8` |  |  |
