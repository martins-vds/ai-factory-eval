# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T13:08:32+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:12:10+00:00 | route-selection-red | 2 | 2.79 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3c22b3dd08b5d414` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-21T13:12:52+00:00 | route-selection-green | 1 | 1.62 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `a65a638d623bdce2` | E       AttributeError: 'Repository' object has no attribute 'upsert' |  |
| 2026-11-21T13:13:00+00:00 | route-selection-green | 0 | 1.74 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `d6ffdb45571cf2ef` |  |  |
| 2026-11-21T13:13:13+00:00 | route-selection-ruff | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:13:13+00:00 | route-selection-format | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-21T13:13:14+00:00 | route-selection-ui | 0 | 0.46 | `python .migration/harness/tools/check_ui.py` | `2fab799a37e17776` |  | gate=ui scope="templates changed since a135db8cd96803a5692cc2c30e5842fe1c87893c" templates=3 findings=0 |
| 2026-11-21T13:13:14+00:00 | route-selection-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T13:16:01+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:16:01+00:00 | build-django-check | 0 | 0.33 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T13:16:51+00:00 | behavior | 0 | 45.9 | `pytest -q` | `7f9fa2762d21f397` |  |  |
| 2026-11-21T13:16:55+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:16:55+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T13:16:55+00:00 | idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T13:16:55+00:00 | idiom-ui | 0 | 0.49 | `python .migration/harness/tools/check_ui.py` | `2fab799a37e17776` |  | gate=ui scope="templates changed since a135db8cd96803a5692cc2c30e5842fe1c87893c" templates=3 findings=0 |
| 2026-11-21T13:17:43+00:00 | crap-coverage | 0 | 43.73 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `3169353f532ac4c4` |  |  |
| 2026-11-21T13:17:43+00:00 | crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:17:43+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8db7d0bb954dc018` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
| 2026-11-21T13:21:50+00:00 | mutation-changed | 0 | 242.5 | `python .migration/harness/tools/afs-mutation` | `073ba02f36837250` |  | gate=mutation score=0.887 threshold=0.8 killed=55 survived=7 files=1 base=a135db8cd96803a5692cc2c30e5842fe1c87893c |
| 2026-11-21T13:22:43+00:00 | route-selection-hardening | 0 | 1.99 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `9016788f2ea059d6` |  |  |
| 2026-11-21T13:22:47+00:00 | route-selection-hardening-ruff | 1 | 0.01 | `ruff check tests/booking/interfaces/test_route_selection.py src/cargotracker/booking/interfaces/route_selection/views.py` | `d9f9d3d1ebeee413` | Found 1 error. |  |
| 2026-11-21T13:22:54+00:00 | route-selection-hardening-ruff | 0 | 0.01 | `ruff check tests/booking/interfaces/test_route_selection.py src/cargotracker/booking/interfaces/route_selection/views.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:22:54+00:00 | route-selection-hardening-format | 1 | 0.01 | `ruff format --check tests/booking/interfaces/test_route_selection.py src/cargotracker/booking/interfaces/route_selection/views.py` | `ba359405c5e801b0` |  |  |
| 2026-11-21T13:23:02+00:00 | route-selection-hardening-format | 0 | 0.01 | `ruff format --check tests/booking/interfaces/test_route_selection.py src/cargotracker/booking/interfaces/route_selection/views.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-21T13:26:28+00:00 | mutation-changed | 0 | 206.39 | `python .migration/harness/tools/afs-mutation` | `17b51c5f73f5ef67` |  | gate=mutation score=0.935 threshold=0.8 killed=58 survived=4 files=1 base=a135db8cd96803a5692cc2c30e5842fe1c87893c |
| 2026-11-21T13:27:23+00:00 | behavior | 0 | 43.53 | `pytest -q` | `f1c6c4f580adf451` |  |  |
| 2026-11-21T13:27:29+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:27:29+00:00 | build-django-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T13:27:29+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:27:29+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T13:27:29+00:00 | idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T13:27:30+00:00 | idiom-ui | 0 | 0.49 | `python .migration/harness/tools/check_ui.py` | `2fab799a37e17776` |  | gate=ui scope="templates changed since a135db8cd96803a5692cc2c30e5842fe1c87893c" templates=3 findings=0 |
| 2026-11-21T13:28:18+00:00 | crap-coverage | 0 | 45.17 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `938039fa92a8b5e3` |  |  |
| 2026-11-21T13:28:18+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:28:18+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `dc8a2783869f1a5a` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
| 2026-11-21T13:29:10+00:00 | regression | 0 | 42.05 | `pytest -q` | `3d82cedd43a89d47` |  |  |
