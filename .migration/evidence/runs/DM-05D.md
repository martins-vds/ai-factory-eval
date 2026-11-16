# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T02:00:16+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:03:25+00:00 | export-red | 1 | 1.85 | `python -m pytest -q tests/data_migration/test_export.py` | `bf8f7730b08cb74a` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-16T02:04:16+00:00 | export-green | 0 | 1.57 | `python -m pytest -q tests/data_migration/test_export.py` | `313e5831c83bcc34` |  |  |
| 2026-11-16T02:04:53+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:04:53+00:00 | build-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T02:04:53+00:00 | idiom-lint | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T02:04:53+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `81f34237d741babf` |  |  |
| 2026-11-16T02:05:07+00:00 | idiom-format-rerun | 0 | 0.01 | `ruff format --check` | `c7a0bcb17dd5241a` |  |  |
| 2026-11-16T02:05:09+00:00 | export-regression | 0 | 1.52 | `python -m pytest -q tests/data_migration/test_export.py` | `7bc5776d19eed069` |  |  |
| 2026-11-16T02:05:20+00:00 | build-compile-final | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:05:21+00:00 | build-check-final | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T02:05:21+00:00 | idiom-lint-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T02:05:21+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `c7a0bcb17dd5241a` |  |  |
| 2026-11-16T02:06:08+00:00 | behavior | 0 | 42.93 | `pytest -q` | `51873e40ccbf6e7c` |  |  |
| 2026-11-16T02:06:50+00:00 | crap-coverage | 0 | 37.26 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `a57eccdd2a64d23e` |  |  |
| 2026-11-16T02:06:50+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:06:50+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `4309ddda1a3b8cc0` |  | gate=crap max=26.0 threshold=30 over=0 methods=185 |
| 2026-11-16T02:08:06+00:00 | mutation-changed | 1 | 71.12 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `ecb04ecb4ea20cbd` | afs-mutation: FAILED score=0.620 threshold=0.8 killed=49 survived=30 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.620 threshold=0.8 killed=49 survived=30 files=1 base=origin/main |
| 2026-11-16T02:09:45+00:00 | export-edge-tests | 1 | 1.67 | `pytest -q tests/data_migration/test_export.py` | `63c96f9786662397` | E           AssertionError: Regex pattern did not match. |  |
| 2026-11-16T02:10:06+00:00 | export-edge-rerun | 0 | 1.66 | `pytest -q tests/data_migration/test_export.py` | `7bbfa9adac667373` |  |  |
| 2026-11-16T02:11:31+00:00 | mutation-changed-rerun | 1 | 70.2 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `0c3ab156031d5d17` | afs-mutation: FAILED score=0.762 threshold=0.8 killed=61 survived=19 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.762 threshold=0.8 killed=61 survived=19 files=1 base=origin/main |
