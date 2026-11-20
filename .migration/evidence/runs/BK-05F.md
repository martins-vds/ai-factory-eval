# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-20T00:34:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:41:23+00:00 | red-route-selection | 2 | 3.45 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `30118c578d2b7565` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-20T00:42:43+00:00 | route-selection-tests | 0 | 4.55 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `48deeaacfc209ce4` |  |  |
| 2026-11-20T00:43:28+00:00 | route-selection-tests | 0 | 4.72 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `4912e2b6b711d5ba` |  |  |
| 2026-11-20T00:43:34+00:00 | ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:43:39+00:00 | ruff-format-check | 1 | 0.02 | `ruff format --check` | `20f5a8ba78c18ce5` | 42 \|                     error='Select a route shown on this page.', |  |
| 2026-11-20T00:43:55+00:00 | ruff-format-check | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T00:49:02+00:00 | build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:49:02+00:00 | build-django-check | 0 | 0.41 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T00:49:07+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:49:07+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T00:49:07+00:00 | idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-20T00:49:08+00:00 | idiom-ui | 0 | 0.61 | `python .migration/harness/tools/check_ui.py` | `339694089709cf19` |  | gate=ui scope="templates changed since 93a9ad8872675fb2aa770724a314257adcf39f1e" templates=1 findings=0 |
| 2026-11-20T00:50:17+00:00 | behavior | 0 | 64.47 | `pytest -q` | `2595eb9594e888e0` |  |  |
| 2026-11-20T00:51:22+00:00 | regression | 0 | 60.62 | `pytest -q` | `ec0ada8b58e674dd` |  |  |
| 2026-11-20T00:52:28+00:00 | crap-coverage | 0 | 59.11 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `97e2e173444c34a5` |  |  |
| 2026-11-20T00:52:28+00:00 | crap-lizard | 0 | 0.17 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:52:28+00:00 | crap-score | 0 | 0.05 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `568138dadd34e9db` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
| 2026-11-20T00:59:35+00:00 | mutation-changed | 1 | 421.85 | `python .migration/harness/tools/afs-mutation` | `f62a45ab8e16cefa` | afs-mutation: FAILED score=0.712 threshold=0.8 killed=42 survived=17 skipped=0 files=1 jobs=1 base=93a9ad8872675fb2aa770 | gate=mutation score=0.712 threshold=0.8 killed=42 survived=17 files=1 base=93a9ad8872675fb2aa770724a314257adcf39f1e |
