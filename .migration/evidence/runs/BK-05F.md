# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:40:41+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:45:42+00:00 | route-ui-red | 2 | 2.44 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `ffa42666eeae0547` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-18T12:46:20+00:00 | route-ui-populated | 0 | 1.97 | `pytest -q tests/booking/interfaces/test_route_selection.py -k route_page_renders_candidate_properties_and_numbered_legs` | `859bfef21b8bd45f` |  |  |
| 2026-11-18T12:47:07+00:00 | itinerary-branches | 1 | 2.43 | `pytest -q tests/booking/interfaces/test_route_selection.py -k select_itinerary` | `9622a3b5152acd53` | assert response.status_code == 200 |  |
| 2026-11-18T12:47:18+00:00 | itinerary-branches-fixed | 0 | 2.38 | `pytest -q tests/booking/interfaces/test_route_selection.py -k select_itinerary` | `5a4c4f51d8231da2` |  |  |
| 2026-11-18T12:47:23+00:00 | assignment-red | 1 | 2.02 | `pytest -q tests/booking/interfaces/test_route_selection.py -k assigning_candidate` | `c9e60655a9c55f0c` | >       assert token is not None |  |
| 2026-11-18T12:48:12+00:00 | route-ui-tests | 0 | 3.59 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3eae56deae2700cc` |  |  |
| 2026-11-18T12:50:48+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:50:52+00:00 | build-django-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T12:50:55+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `aa0b500024bf7ff8` | Found 1 error. |  |
| 2026-11-18T12:51:03+00:00 | idiom-ruff-check-fixed | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:51:06+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `21c2a862c1ecbb9e` | 112 \|     assert 'No routes found that satisfy the route specification.' in content |  |
| 2026-11-18T12:51:26+00:00 | idiom-ruff-format-fixed | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T12:51:31+00:00 | idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:51:35+00:00 | idiom-ui | 0 | 0.4 | `python .migration/harness/tools/check_ui.py` | `5daa3761371821be` |  | gate=ui scope="templates changed since 99d0c67b9ab328eed52a548a30966c81eef0da87" templates=3 findings=0 |
| 2026-11-18T12:52:31+00:00 | crap-coverage | 0 | 50.11 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `01629898cc54ddcc` |  |  |
| 2026-11-18T12:52:37+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:52:40+00:00 | crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `aa63c477ee5ece6f` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-18T12:57:06+00:00 | mutation-changed | 0 | 260.55 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `3b07843fce7abbb9` |  | gate=mutation score=0.811 threshold=0.8 killed=43 survived=10 files=1 base=origin/main |
| 2026-11-18T12:58:21+00:00 | regression | 0 | 45.81 | `pytest -q` | `f4dac5551c3936fb` |  |  |
| 2026-11-18T13:00:08+00:00 | route-tests | 0 | 4.76 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `fa009296896442e9` |  |  |
| 2026-11-18T13:00:22+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:00:22+00:00 | build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T13:00:22+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:00:22+00:00 | idiom-ruff-format | 1 | 0.01 | `ruff format --check` | `0668f329bcfba770` |  |  |
| 2026-11-18T13:00:40+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:00:40+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T13:00:40+00:00 | idiom-layers-final | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:00:41+00:00 | idiom-ui-final | 0 | 0.39 | `python .migration/harness/tools/check_ui.py` | `5daa3761371821be` |  | gate=ui scope="templates changed since 99d0c67b9ab328eed52a548a30966c81eef0da87" templates=3 findings=0 |
| 2026-11-18T13:01:26+00:00 | crap-coverage-final | 0 | 45.53 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `8b160d5149aa57fb` |  |  |
| 2026-11-18T13:01:26+00:00 | crap-lizard-final | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:01:27+00:00 | crap-threshold-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `7788b56d36b25d72` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-18T13:05:35+00:00 | mutation-changed-final | 0 | 248.49 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `75a0ba731cbd5bd1` |  | gate=mutation score=0.868 threshold=0.8 killed=46 survived=7 files=1 base=origin/main |
| 2026-11-18T13:06:23+00:00 | regression-final | 0 | 47.71 | `pytest -q` | `74bca28554622e76` |  |  |
| 2026-11-18T13:07:35+00:00 | build-compile-final | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:07:35+00:00 | build-django-check-final | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T13:07:35+00:00 | idiom-ruff-check-final2 | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:07:36+00:00 | idiom-ruff-format-final2 | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T13:07:36+00:00 | idiom-layers-final2 | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:07:36+00:00 | idiom-ui-final2 | 0 | 0.39 | `python .migration/harness/tools/check_ui.py` | `5daa3761371821be` |  | gate=ui scope="templates changed since 99d0c67b9ab328eed52a548a30966c81eef0da87" templates=3 findings=0 |
| 2026-11-18T13:08:23+00:00 | crap-coverage-final2 | 0 | 46.92 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `3f60a20d75835e28` |  |  |
| 2026-11-18T13:08:23+00:00 | crap-lizard-final2 | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:08:24+00:00 | crap-threshold-final2 | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `7788b56d36b25d72` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-18T13:12:26+00:00 | mutation-changed-final2 | 0 | 242.07 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `b9f85756107ebb82` |  | gate=mutation score=0.887 threshold=0.8 killed=47 survived=6 files=1 base=origin/main |
| 2026-11-18T13:13:11+00:00 | regression-final2 | 0 | 45.59 | `pytest -q` | `74578b7ba71a8ba7` |  |  |
| 2026-11-18T13:13:29+00:00 | migration-validate | 0 | 3.9 | `python .migration/harness/tools/validate.py .migration` | `ef34805838431398` |  |  |
| 2026-11-18T15:42:53+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
