# Run journal: REF-01

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T04:24:57+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:26:29+00:00 | tdd-red-schema-api | 2 | 3.64 | `pytest -q tests/data_migration/test_export.py` | `39c8a7f65b64fee1` | _____________ ERROR collecting tests/data_migration/test_export.py _____________ |  |
| 2026-11-22T04:26:55+00:00 | focused-export-tests | 0 | 2.56 | `pytest -q tests/data_migration/test_export.py` | `a8ae3ff2db0d1bfc` |  |  |
| 2026-11-22T04:27:18+00:00 | build-compile | 0 | 0.08 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:27:19+00:00 | build-django-check | 0 | 0.41 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T04:28:38+00:00 | behavior | 0 | 77.38 | `pytest -q` | `6b40997efc8b47b1` |  |  |
| 2026-11-22T04:28:41+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T04:28:41+00:00 | idiom-ruff-format | 0 | 0.03 | `ruff format --check` | `b221fa32ed80fb2e` |  |  |
| 2026-11-22T04:28:42+00:00 | idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `59bfd54275a9b5a4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-22T04:28:42+00:00 | idiom-ui | 0 | 0.7 | `python .migration/harness/tools/check_ui.py` | `50d3f910dff66d78` |  | gate=ui scope="templates changed since 1bc7875fe513f393ea9c7de89707628f18827520" templates=0 findings=0 |
| 2026-11-22T04:30:02+00:00 | crap-coverage | 0 | 75.14 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `fd5d7d99a7f5f542` |  |  |
| 2026-11-22T04:30:02+00:00 | crap-lizard | 0 | 0.18 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:30:02+00:00 | crap-threshold | 0 | 0.05 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `049badc57b42932f` |  | gate=crap max=26.0 threshold=30 over=0 methods=213 |
| 2026-11-22T04:31:33+00:00 | mutation-changed | 0 | 86.65 | `python .migration/harness/tools/afs-mutation` | `3393fd28296159d3` |  | gate=mutation score=0.978 threshold=0.8 killed=90 survived=2 files=2 base=1bc7875fe513f393ea9c7de89707628f18827520 |
| 2026-11-22T04:33:27+00:00 | regression | 0 | 75.05 | `pytest -q` | `0d919714cf221da3` |  |  |
