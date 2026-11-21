# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T02:41:06+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T02:42:15+00:00 | red-route-selection | 2 | 1.06 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `aee4e96eb7705ab5` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-21T02:42:40+00:00 | green-route-selection | 1 | 2.84 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `100e95f2aab95afe` | assert cargo is not None |  |
| 2026-11-21T02:42:49+00:00 | green-route-selection | 0 | 2.81 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `da1f270e4d1c9870` |  |  |
| 2026-11-21T02:43:40+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T02:43:41+00:00 | build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T02:43:44+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `88cf015c081e1797` | Found 1 error. |  |
| 2026-11-21T02:43:50+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T02:43:50+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T02:43:51+00:00 | idiom-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T02:43:51+00:00 | idiom-ui | 0 | 0.46 | `python .migration/harness/tools/check_ui.py` | `37861f3417f2f49b` |  | gate=ui scope="templates changed since fc3bb05ed7ecde78b513097e7cd63a7ae0095ce3" templates=2 findings=0 |
| 2026-11-21T02:45:35+00:00 | behavior-route-selection-review | 0 | 2.81 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `da1f270e4d1c9870` |  |  |
| 2026-11-21T02:46:30+00:00 | behavior-full-suite | 0 | 46.85 | `pytest -q` | `e0aab21e24f70dfd` |  |  |
| 2026-11-21T02:47:18+00:00 | crap-coverage | 0 | 43.98 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `a928fd06cf7c76fd` |  |  |
| 2026-11-21T02:47:18+00:00 | crap-lizard | 0 | 0.12 | `lizard --csv src` | `310158a423e5765a` | 16,3,86,6,16,"_origin_step@38-53@src/cargotracker/booking/interfaces/wizard/views.py","src/cargotracker/booking/interfac |  |
| 2026-11-21T02:47:18+00:00 | crap-score | 1 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `1f315dff0c7b9238` |  |  |
| 2026-11-21T02:47:31+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T02:48:30+00:00 | mutation-changed | 1 | 53.49 | `python .migration/harness/tools/afs-mutation` | `498aa63bbaae2df7` | afs-mutation: FAILED score=0.742 threshold=0.8 killed=23 survived=8 skipped=0 files=1 jobs=1 base=fc3bb05ed7ecde78b51309 | gate=mutation score=0.742 threshold=0.8 killed=23 survived=8 files=1 base=fc3bb05ed7ecde78b513097e7cd63a7ae0095ce3 |
| 2026-11-21T02:48:56+00:00 | behavior-route-selection-mutation-tests | 1 | 4.48 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `d3d7a1b001312a1a` | E       RuntimeError: Database access not allowed, use the "django_db" mark, or the "db" or "transactional_db" fixtures  |  |
| 2026-11-21T02:49:08+00:00 | behavior-route-selection-mutation-tests | 0 | 4.28 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3f9186955a09af76` |  |  |
| 2026-11-21T02:50:12+00:00 | mutation-changed | 0 | 61.55 | `python .migration/harness/tools/afs-mutation` | `0be65aea57e0c900` |  | gate=mutation score=0.968 threshold=0.8 killed=30 survived=1 files=1 base=fc3bb05ed7ecde78b513097e7cd63a7ae0095ce3 |
| 2026-11-21T02:51:03+00:00 | regression-full-suite-final | 0 | 45.36 | `pytest -q` | `b646576d611a9ac6` |  |  |
| 2026-11-21T02:51:03+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T02:51:03+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T02:51:03+00:00 | idiom-layers-final | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T02:51:04+00:00 | idiom-ui-final | 0 | 0.47 | `python .migration/harness/tools/check_ui.py` | `16b6e629c72920bf` |  | gate=ui scope="templates changed since fc3bb05ed7ecde78b513097e7cd63a7ae0095ce3" templates=3 findings=0 |
| 2026-11-21T02:51:27+00:00 | build-compile-final | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T02:51:27+00:00 | build-django-check-final | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
