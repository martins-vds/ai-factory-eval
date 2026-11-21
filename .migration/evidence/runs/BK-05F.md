# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T18:52:50+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T18:59:06+00:00 | behavior-red | 2 | 2.74 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `a1f56ea0cf988b91` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-21T19:00:13+00:00 | behavior-green | 1 | 1.54 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `8bb6903f36d8beca` | E       NameError: name 'DjangoCargoRepository' is not defined |  |
| 2026-11-21T19:00:24+00:00 | behavior-green-2 | 1 | 1.7 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `daaff3ace1c19e55` | assert route_response.status_code == 200 |  |
| 2026-11-21T19:00:34+00:00 | behavior-green-3 | 0 | 1.65 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `9bed9041f3a97041` |  |  |
| 2026-11-21T19:00:51+00:00 | lint-focused | 1 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `442d6ffc5b5b97b5` |  |  |
| 2026-11-21T19:01:10+00:00 | lint-details | 1 | 0.01 | `ruff check --output-format concise src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `47778d01717857fb` |  |  |
| 2026-11-21T19:01:36+00:00 | behavior-green-final | 0 | 1.68 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `8ef3627370199135` |  |  |
| 2026-11-21T19:01:39+00:00 | lint-focused-final | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:01:49+00:00 | format-focused | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-21T19:01:53+00:00 | ui-focused | 1 | 0.41 | `python .migration/harness/tools/check_ui.py --all` | `7bd7afd4e4c90bd7` | templates/admin/live_map.html:34: sends an htmx request ('hx-get'), but nothing handles error responses: htmx swaps no 4 | gate=ui scope="every template" templates=20 findings=3 |
| 2026-11-21T19:05:03+00:00 | behavior-edge-cases | 0 | 1.84 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `f30da780d3c971fc` |  |  |
| 2026-11-21T19:05:26+00:00 | lint-edge-final | 1 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `4498a45a1c93b472` | Found 1 error. |  |
| 2026-11-21T19:05:32+00:00 | lint-edge-final-2 | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:05:35+00:00 | format-edge-final | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-21T19:05:37+00:00 | ui-changed-final | 0 | 0.42 | `python .migration/harness/tools/check_ui.py --changed-since 1d9da909` | `7123d121e6fe05b7` |  | gate=ui scope="templates changed since 1d9da909" templates=4 findings=0 |
| 2026-11-21T19:06:18+00:00 | migration-state-validation | 0 | 4.32 | `python .migration/harness/tools/validate.py .migration` | `6fb607b073658220` |  |  |
| 2026-11-21T19:06:32+00:00 | build-compileall | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:06:35+00:00 | build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T19:07:24+00:00 | behavior-suite | 0 | 45.15 | `pytest -q` | `1d26b086940341f0` |  |  |
| 2026-11-21T19:07:27+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:07:29+00:00 | idiom-format-check | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T19:07:32+00:00 | idiom-layers | 0 | 0.11 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T19:07:36+00:00 | idiom-ui | 0 | 0.43 | `python .migration/harness/tools/check_ui.py` | `6c483fb5a08ad33e` |  | gate=ui scope="templates changed since 36fae5a689c9209c673e36ecb81a55398131911e" templates=4 findings=0 |
| 2026-11-21T19:08:28+00:00 | crap-coverage-suite | 0 | 46.52 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `d4f47d48230426e9` |  |  |
| 2026-11-21T19:08:31+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:08:33+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T19:09:31+00:00 | mutation-changed | 0 | 54.75 | `python .migration/harness/tools/afs-mutation` | `d846f808b9d3d0c5` |  | gate=mutation score=0.830 threshold=0.8 killed=44 survived=9 files=1 base=36fae5a689c9209c673e36ecb81a55398131911e |
| 2026-11-21T19:10:14+00:00 | behavior-security-edges | 0 | 1.96 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `004181ebcbfe5d9e` |  |  |
| 2026-11-21T19:10:19+00:00 | lint-edge-guards | 0 | 0.01 | `ruff check tests/booking/interfaces/test_route_selection.py src/cargotracker/booking/interfaces/route_selection/views.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:10:21+00:00 | format-edge-guards | 0 | 0.01 | `ruff format --check tests/booking/interfaces/test_route_selection.py src/cargotracker/booking/interfaces/route_selection/views.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-21T19:11:29+00:00 | mutation-changed-final | 0 | 56.22 | `python .migration/harness/tools/afs-mutation` | `543f58b416ca63f8` |  | gate=mutation score=0.849 threshold=0.8 killed=45 survived=8 files=1 base=36fae5a689c9209c673e36ecb81a55398131911e |
| 2026-11-21T19:11:51+00:00 | behavior-empty-and-methods | 0 | 1.99 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `39292d5bd4c6e671` |  |  |
| 2026-11-21T19:11:54+00:00 | lint-final-tests | 0 | 0.01 | `ruff check tests/booking/interfaces/test_route_selection.py src/cargotracker/booking/interfaces/route_selection/views.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:11:56+00:00 | format-final-tests | 0 | 0.01 | `ruff format --check tests/booking/interfaces/test_route_selection.py src/cargotracker/booking/interfaces/route_selection/views.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-21T19:13:10+00:00 | mutation-changed-final-2 | 0 | 56.34 | `python .migration/harness/tools/afs-mutation` | `8307dc2cf301bcb3` |  | gate=mutation score=0.906 threshold=0.8 killed=48 survived=5 files=1 base=36fae5a689c9209c673e36ecb81a55398131911e |
| 2026-11-21T19:14:18+00:00 | final-build-compileall | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:14:21+00:00 | final-build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T19:15:17+00:00 | final-behavior-suite | 0 | 53.74 | `pytest -q` | `23514f8a576d623c` |  |  |
| 2026-11-21T19:15:20+00:00 | final-idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:15:22+00:00 | final-idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T19:15:25+00:00 | final-idiom-layers | 0 | 0.11 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T19:15:28+00:00 | final-idiom-ui | 0 | 0.44 | `python .migration/harness/tools/check_ui.py` | `6c483fb5a08ad33e` |  | gate=ui scope="templates changed since 36fae5a689c9209c673e36ecb81a55398131911e" templates=4 findings=0 |
| 2026-11-21T19:16:17+00:00 | final-crap-coverage | 0 | 45.43 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `ec80485fe0e0e4bb` |  |  |
| 2026-11-21T19:16:20+00:00 | final-crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:16:23+00:00 | final-crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T19:17:14+00:00 | final-regression-suite | 0 | 47.26 | `pytest -q` | `067ac03a75e29767` |  |  |
| 2026-11-21T19:18:08+00:00 | final-migration-validation | 0 | 4.51 | `python .migration/harness/tools/validate.py .migration` | `ef34805838431398` |  |  |
