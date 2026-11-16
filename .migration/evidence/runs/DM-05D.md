# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T03:58:09+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T04:00:55+00:00 | export-red | 1 | 2.25 | `python -m pytest -q tests/data_migration/test_export.py` | `993e34b993731366` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-16T04:01:29+00:00 | export-tests | 0 | 1.85 | `python -m pytest -q tests/data_migration/test_export.py` | `263c94f24c6bf4b6` |  |  |
| 2026-11-16T04:01:41+00:00 | idiom-lint-targeted | 1 | 0.01 | `ruff check src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `43b474df297a441d` | 62 \|     assert carrier_movement['departure_time'] == '2026-11-08T12:00:00Z' |  |
| 2026-11-16T04:01:41+00:00 | idiom-format-targeted | 1 | 0.01 | `ruff format --check src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `4b0b9321e6532ba2` | 44 \|     except OSError as error: |  |
| 2026-11-16T04:01:52+00:00 | format-targeted | 0 | 0.01 | `ruff format src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `10869b88a75066aa` |  |  |
| 2026-11-16T04:01:56+00:00 | idiom-format-targeted-rerun | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-16T04:01:56+00:00 | idiom-lint-targeted-rerun | 0 | 0.01 | `ruff check src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T04:01:58+00:00 | export-tests-rerun | 0 | 1.87 | `python -m pytest -q tests/data_migration/test_export.py` | `67c681089d32fd8f` |  |  |
| 2026-11-16T04:02:47+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T04:02:47+00:00 | build-django-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T04:02:52+00:00 | idiom-lint | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T04:02:52+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `c7a0bcb17dd5241a` |  |  |
| 2026-11-16T04:03:44+00:00 | behavior | 0 | 49.34 | `pytest -q` | `20e205c2ee35240c` |  |  |
| 2026-11-16T04:04:53+00:00 | crap-coverage | 0 | 61.06 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `648a4a81c6fadf60` |  |  |
| 2026-11-16T04:05:18+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T04:05:19+00:00 | crap-threshold | 0 | 0.05 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `b7506f3f036368bb` |  | gate=crap max=26.0 threshold=30 over=0 methods=181 |
| 2026-11-16T04:23:43+00:00 | mutation-changed-retry | 1 | 59.56 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `6fde90a8086f18ae` | afs-mutation: FAILED score=0.655 threshold=0.8 killed=36 survived=19 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.655 threshold=0.8 killed=36 survived=19 files=1 base=origin/main |
| 2026-11-16T04:25:22+00:00 | export-survivor-tests | 0 | 2.03 | `python -m pytest -q tests/data_migration/test_export.py` | `7edfb975894be936` |  |  |
| 2026-11-16T04:25:31+00:00 | survivor-tests-lint | 0 | 0.01 | `ruff check src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T04:25:31+00:00 | survivor-tests-format | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-16T04:26:48+00:00 | mutation-changed-final | 0 | 60.77 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `87d10758bc49d1c5` |  | gate=mutation score=0.836 threshold=0.8 killed=46 survived=9 files=1 base=origin/main |
| 2026-11-16T04:28:09+00:00 | behavior-final | 0 | 58.5 | `pytest -q` | `d4857502e08a91db` |  |  |
| 2026-11-16T04:29:20+00:00 | regression | 0 | 66.1 | `pytest -q` | `07be86d797daacd6` |  |  |
| 2026-11-16T04:30:49+00:00 | crap-coverage-final | 0 | 58.91 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `c646842c8df6f899` |  |  |
| 2026-11-16T04:30:49+00:00 | crap-lizard-final | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T04:30:49+00:00 | crap-threshold-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `7413ee0e3541288b` |  | gate=crap max=26.0 threshold=30 over=0 methods=181 |
