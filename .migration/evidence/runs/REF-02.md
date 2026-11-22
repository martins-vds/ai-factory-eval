# Run journal: REF-02

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T04:22:25+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:23:07+00:00 | baseline-fee-tests | 0 | 14.1 | `pytest -q tests/fees/test_endpoints.py` | `55e2afd6cb0b6e16` |  |  |
| 2026-11-22T04:24:03+00:00 | post-refactor-fee-tests | 0 | 10.43 | `pytest -q tests/fees/test_endpoints.py` | `f78a1627acfedf42` |  |  |
| 2026-11-22T04:24:14+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:24:15+00:00 | build-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T04:24:15+00:00 | idiom-lint | 0 | 0.01 | `ruff check src config manage.py tests` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T04:24:15+00:00 | idiom-format | 0 | 0.01 | `ruff format --check src config manage.py tests` | `aec51819fa2b338a` |  |  |
| 2026-11-22T04:24:15+00:00 | idiom-layers | 0 | 0.07 | `python .migration/harness/tools/check_layers.py` | `9d7cc80d2e3da394` |  | gate=layering contracts=1 violations=0 known=0 |
| 2026-11-22T04:24:16+00:00 | idiom-ui | 0 | 0.36 | `python .migration/harness/tools/check_ui.py` | `21957b2932b007df` |  | gate=ui scope="templates changed since 95c93517d57c327c9282a0d604ca3bf7bb50d0a7" templates=0 findings=0 |
| 2026-11-22T04:24:31+00:00 | behavior | 0 | 13.86 | `pytest -q` | `a6d5667670ef51d6` |  |  |
| 2026-11-22T04:24:49+00:00 | crap-coverage | 0 | 14.64 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `bdd3a3955b2c4d6a` |  |  |
| 2026-11-22T04:24:49+00:00 | crap-lizard | 0 | 0.06 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:24:49+00:00 | crap-threshold | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `d6c4a1ceec81d5f9` |  | gate=crap max=7.0 threshold=30 over=0 methods=46 |
| 2026-11-22T04:29:34+00:00 | mutation-changed | 0 | 282.79 | `python .migration/harness/tools/afs-mutation` | `6b5c566a0f23fa75` |  | gate=mutation score=1.000 threshold=0.8 killed=61 survived=0 files=2 base=95c93517d57c327c9282a0d604ca3bf7bb50d0a7 |
| 2026-11-22T04:29:50+00:00 | regression | 0 | 13.39 | `pytest -q` | `c0e4b1e5aded2688` |  |  |
