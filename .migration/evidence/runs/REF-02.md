# Run journal: REF-02

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T14:40:21+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T14:41:09+00:00 | behavior-baseline | 0 | 13.61 | `pytest -q tests/fees` | `bdb3bc6cd47fc5f2` |  |  |
| 2026-11-22T14:41:54+00:00 | behavior-smoke | 0 | 10.41 | `pytest -q tests/fees` | `3219fe1a504f9bbf` |  |  |
| 2026-11-22T14:42:19+00:00 | build | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T14:42:19+00:00 | build | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T14:42:33+00:00 | behavior | 0 | 14.02 | `pytest -q` | `41fb8037838f1ef8` |  |  |
| 2026-11-22T14:42:33+00:00 | idiom | 0 | 0.01 | `ruff check src config manage.py tests` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T14:42:33+00:00 | idiom | 0 | 0.01 | `ruff format --check src config manage.py tests` | `aec51819fa2b338a` |  |  |
| 2026-11-22T14:42:33+00:00 | idiom | 0 | 0.08 | `python .migration/harness/tools/check_layers.py` | `9d7cc80d2e3da394` |  | gate=layering contracts=1 violations=0 known=0 |
| 2026-11-22T14:42:34+00:00 | idiom | 0 | 0.49 | `python .migration/harness/tools/check_ui.py` | `8c190a9497b29358` |  | gate=ui scope="templates changed since 4074f47648bf007da887d9bfa5cbfecff8592563" templates=0 findings=0 |
| 2026-11-22T14:43:02+00:00 | crap | 0 | 14.96 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `9329559451017863` |  |  |
| 2026-11-22T14:43:02+00:00 | crap | 0 | 0.07 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T14:43:02+00:00 | crap | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `83ebbbceb3fb7d75` |  | gate=crap max=7.0 threshold=30 over=0 methods=46 |
| 2026-11-22T14:47:59+00:00 | mutation_changed | 0 | 283.23 | `python .migration/harness/tools/afs-mutation` | `a42fb628d765611b` |  | gate=mutation score=1.000 threshold=0.8 killed=61 survived=0 files=2 base=4074f47648bf007da887d9bfa5cbfecff8592563 |
| 2026-11-22T14:48:48+00:00 | behavior-smoke-final | 0 | 10.5 | `pytest -q tests/fees` | `43a3558982da3b0e` |  |  |
| 2026-11-22T14:49:01+00:00 | build | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T14:49:01+00:00 | build | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T14:49:15+00:00 | behavior | 0 | 14.16 | `pytest -q` | `4b4f70f906b13ac8` |  |  |
| 2026-11-22T14:49:15+00:00 | idiom | 0 | 0.01 | `ruff check src config manage.py tests` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T14:49:15+00:00 | idiom | 0 | 0.01 | `ruff format --check src config manage.py tests` | `aec51819fa2b338a` |  |  |
| 2026-11-22T14:49:15+00:00 | idiom | 0 | 0.08 | `python .migration/harness/tools/check_layers.py` | `9d7cc80d2e3da394` |  | gate=layering contracts=1 violations=0 known=0 |
| 2026-11-22T14:49:16+00:00 | idiom | 0 | 0.45 | `python .migration/harness/tools/check_ui.py` | `8c190a9497b29358` |  | gate=ui scope="templates changed since 4074f47648bf007da887d9bfa5cbfecff8592563" templates=0 findings=0 |
| 2026-11-22T14:49:31+00:00 | crap | 0 | 14.9 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `36c17a5a2578397f` |  |  |
| 2026-11-22T14:49:31+00:00 | crap | 0 | 0.07 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T14:49:31+00:00 | crap | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `4f180f48bf44945e` |  | gate=crap max=7.0 threshold=30 over=0 methods=46 |
