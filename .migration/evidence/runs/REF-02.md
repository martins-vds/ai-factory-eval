# Run journal: REF-02

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T14:31:02+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T14:32:14+00:00 | targeted-idiom | 0 | 0.01 | `ruff check src/fees/views.py src/fees/presentation.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T14:32:25+00:00 | targeted-behavior | 0 | 11.25 | `pytest -q tests/fees/test_endpoints.py tests/fees/test_fee_calculation.py` | `baaf8873140f4e34` |  |  |
| 2026-11-22T14:32:47+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T14:32:51+00:00 | build-check | 0 | 0.34 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T14:33:08+00:00 | behavior | 0 | 15.04 | `pytest -q` | `f26fcfb546fbd6ca` |  |  |
| 2026-11-22T14:33:10+00:00 | spec | 0 | 0.72 | `python .migration/harness/tools/afs-spec run` | `f73c1e46c2365835` | AFS-RESULT gate=spec cases=10 failed=0 pending=0 | gate=spec cases=10 failed=0 pending=0 |
| 2026-11-22T14:33:13+00:00 | idiom-ruff | 0 | 0.01 | `ruff check src config manage.py tests` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T14:33:16+00:00 | idiom-format | 0 | 0.01 | `ruff format --check src config manage.py tests` | `aec51819fa2b338a` |  |  |
| 2026-11-22T14:33:17+00:00 | idiom-layers | 0 | 0.1 | `python .migration/harness/tools/check_layers.py` | `9d7cc80d2e3da394` |  | gate=layering contracts=1 violations=0 known=0 |
| 2026-11-22T14:33:20+00:00 | idiom-ui | 0 | 0.6 | `python .migration/harness/tools/check_ui.py` | `cf777cc20105ab95` |  | gate=ui scope="templates changed since 08c7e48386a66afa31857cd8105f98bc17dd8523" templates=0 findings=0 |
| 2026-11-22T14:33:39+00:00 | crap-coverage | 0 | 15.96 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `03e71023c8d2aa5c` |  |  |
| 2026-11-22T14:33:41+00:00 | crap-lizard | 0 | 0.08 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T14:33:43+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `83ebbbceb3fb7d75` |  | gate=crap max=7.0 threshold=30 over=0 methods=46 |
| 2026-11-22T14:38:36+00:00 | mutation-changed | 0 | 290.63 | `python .migration/harness/tools/afs-mutation` | `0d8c13728e3e71d8` |  | gate=mutation score=1.000 threshold=0.8 killed=61 survived=0 files=2 base=08c7e48386a66afa31857cd8105f98bc17dd8523 |
| 2026-11-22T14:38:56+00:00 | regression | 0 | 14.93 | `pytest -q` | `92bf896ce99b8bf7` |  |  |
