# Run journal: REF-02

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T04:24:56+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:25:46+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:25:47+00:00 | build-django-check | 0 | 0.98 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T04:25:57+00:00 | behavior-focused | 0 | 11.48 | `pytest -q tests/fees/test_endpoints.py tests/fees/test_fee_calculation.py` | `907b96b79c505949` |  |  |
| 2026-11-22T04:26:30+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check src config manage.py tests` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T04:26:30+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check src config manage.py tests` | `aec51819fa2b338a` |  |  |
| 2026-11-22T04:26:30+00:00 | idiom-layers | 0 | 0.08 | `python .migration/harness/tools/check_layers.py` | `9d7cc80d2e3da394` |  | gate=layering contracts=1 violations=0 known=0 |
| 2026-11-22T04:26:30+00:00 | idiom-ui | 0 | 0.34 | `python .migration/harness/tools/check_ui.py` | `c36a705ec9dfc1e1` |  | gate=ui scope="templates changed since 4ebf9bb63e287197ad5ee34d054b1b7122f9a589" templates=0 findings=0 |
| 2026-11-22T04:26:47+00:00 | crap-coverage | 0 | 14.12 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `b1d2435d153f8567` |  |  |
| 2026-11-22T04:26:49+00:00 | crap-lizard | 0 | 0.05 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:26:51+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `83ebbbceb3fb7d75` |  | gate=crap max=7.0 threshold=30 over=0 methods=46 |
| 2026-11-22T04:31:29+00:00 | mutation-changed | 0 | 274.75 | `python .migration/harness/tools/afs-mutation` | `2f0788ed404d30db` |  | gate=mutation score=1.000 threshold=0.8 killed=61 survived=0 files=2 base=4ebf9bb63e287197ad5ee34d054b1b7122f9a589 |
| 2026-11-22T04:31:44+00:00 | regression | 0 | 13.3 | `pytest -q` | `a027c9a60c74bb65` |  |  |
