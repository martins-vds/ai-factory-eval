# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:47+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T23:10:51+00:00 | route-ui-populated-red | 4 | 2.65 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_selection_renders_populated_candidates_and_numbered_legs` | `b4cc25268b09cfd2` | ERROR: found no collectors for /home/runner/work/ai-factory-pilot-target/ai-factory-pilot-target/tests/booking/interface |  |
| 2026-11-07T23:11:21+00:00 | route-ui-populated-green | 1 | 1.44 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_selection_renders_populated_candidates_and_numbered_legs` | `30e0c6f92a86ec56` | assert response.status_code == 200 |  |
| 2026-11-07T23:11:30+00:00 | route-ui-populated-green | 0 | 1.44 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_selection_renders_populated_candidates_and_numbered_legs` | `f51873a8b2568bb4` |  |  |
| 2026-11-07T23:11:57+00:00 | route-ui-empty-state | 0 | 1.45 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_explain_when_no_candidates_satisfy_the_deadline` | `baa6efe8d11cd56d` |  |  |
| 2026-11-07T23:12:05+00:00 | select-itinerary-candidates | 0 | 1.47 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_select_itinerary_renders_candidate_routes_when_available` | `7b23e52dabef120c` |  |  |
| 2026-11-07T23:12:16+00:00 | route-assignment-red | 1 | 1.5 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_assigning_candidate_redirects_to_details_with_the_selected_itinerary` | `d87db90c076ef66a` | E       IndexError: list index out of range |  |
| 2026-11-07T23:12:40+00:00 | route-assignment-green | 0 | 1.45 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_assigning_candidate_redirects_to_details_with_the_selected_itinerary` | `baa6efe8d11cd56d` |  |  |
| 2026-11-07T23:12:50+00:00 | route-ui-tests | 0 | 1.61 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `7bbfa9adac667373` |  |  |
| 2026-11-07T23:13:36+00:00 | route-ui-focused-tests | 0 | 1.79 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `8c4b2d4a4d13e6aa` |  |  |
| 2026-11-07T23:14:04+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T23:14:08+00:00 | build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-07T23:14:11+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-07T23:14:13+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `c3ac60a207092b7f` |  |  |
| 2026-11-07T23:15:02+00:00 | behavior | 0 | 44.5 | `pytest -q` | `2cd8216bb3af3078` |  |  |
| 2026-11-07T23:15:51+00:00 | crap-coverage | 0 | 43.73 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `ee3d9f5a93695ee8` |  |  |
| 2026-11-07T23:15:54+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T23:15:58+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `c1f7b4ca904f936a` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-07T23:16:58+00:00 | mutation-changed | 0 | 56.53 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `0a4bcffd98d4085f` |  | gate=mutation score=0.828 threshold=0.8 killed=48 survived=10 files=1 base=origin/main |
| 2026-11-07T23:19:39+00:00 | no-route-guidance-red | 1 | 1.61 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_explain_when_no_candidates_satisfy_the_deadline` | `45ce6ef361911e1f` | assert route_response.status_code == 200 |  |
| 2026-11-07T23:19:50+00:00 | no-route-guidance-green | 0 | 1.44 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_explain_when_no_candidates_satisfy_the_deadline` | `baa6efe8d11cd56d` |  |  |
| 2026-11-07T23:19:56+00:00 | build-compile-final | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T23:20:00+00:00 | django-check-final | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-07T23:20:04+00:00 | idiom-final | 0 | 0.02 | `bash -c 'ruff check && ruff format --check'` | `07a2e0ea53bd64f2` |  |  |
| 2026-11-07T23:20:10+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-07T23:20:13+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `c3ac60a207092b7f` |  |  |
| 2026-11-07T23:21:07+00:00 | behavior-final | 0 | 51.05 | `pytest -q` | `7c14b01758950b7e` |  |  |
| 2026-11-07T23:21:53+00:00 | crap-coverage-final | 0 | 42.29 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `1bce9f64c07d81f0` |  |  |
| 2026-11-07T23:21:57+00:00 | crap-lizard-final | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T23:21:57+00:00 | crap-score-final | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `c1f7b4ca904f936a` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-07T23:23:01+00:00 | mutation-changed-final | 0 | 59.77 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `94fd5d6e80493ea3` |  | gate=mutation score=0.803 threshold=0.8 killed=49 survived=12 files=1 base=origin/main |
| 2026-11-07T23:23:22+00:00 | http-method-test | 0 | 1.41 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_reject_unsupported_http_methods` | `a558b8376cd28466` |  |  |
| 2026-11-07T23:24:09+00:00 | behavior-after-http-test | 0 | 43.77 | `pytest -q` | `2031f4ad9510cea0` |  |  |
| 2026-11-07T23:25:14+00:00 | mutation-changed-final | 0 | 61.09 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `94fd5d6e80493ea3` |  | gate=mutation score=0.803 threshold=0.8 killed=49 survived=12 files=1 base=origin/main |
| 2026-11-07T23:25:33+00:00 | http-method-test-valid-cargo | 0 | 1.5 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_reject_unsupported_http_methods` | `f51873a8b2568bb4` |  |  |
| 2026-11-07T23:26:42+00:00 | mutation-changed-final | 0 | 64.58 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `94fd5d6e80493ea3` |  | gate=mutation score=0.803 threshold=0.8 killed=49 survived=12 files=1 base=origin/main |
| 2026-11-07T23:27:47+00:00 | behavior-final-467 | 0 | 45.11 | `pytest -q` | `c26d6d9b6bcf9177` |  |  |
| 2026-11-07T23:29:04+00:00 | crap-coverage-final-467 | 0 | 46.55 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `aeae45f0cde2980f` |  |  |
| 2026-11-07T23:29:08+00:00 | crap-lizard-final-467 | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T23:29:08+00:00 | crap-score-final-467 | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `c1f7b4ca904f936a` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-07T23:30:38+00:00 | route-redirect-sanitization-test | 0 | 1.56 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_assigning_candidate_redirects_to_details_with_the_selected_itinerary` | `7cfbd4174b4e5fac` |  |  |
| 2026-11-07T23:30:44+00:00 | build-compile-security-fix | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T23:30:49+00:00 | django-check-security-fix | 0 | 0.32 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-07T23:30:53+00:00 | idiom-security-fix-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-07T23:30:58+00:00 | idiom-security-fix-format | 0 | 0.01 | `ruff format --check` | `c3ac60a207092b7f` |  |  |
| 2026-11-07T23:31:47+00:00 | behavior-security-fix | 0 | 44.76 | `pytest -q` | `72ce2532210dcc23` |  |  |
| 2026-11-07T23:32:37+00:00 | crap-coverage-security-fix | 0 | 42.91 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `3ccac7a1bf25cd16` |  |  |
| 2026-11-07T23:32:41+00:00 | crap-lizard-security-fix | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T23:32:41+00:00 | crap-score-security-fix | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `c1f7b4ca904f936a` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-07T23:33:57+00:00 | mutation-changed-security-fix | 1 | 61.57 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `6587d75718117f99` | afs-mutation: FAILED score=0.790 threshold=0.8 killed=49 survived=13 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.790 threshold=0.8 killed=49 survived=13 files=1 base=origin/main |
| 2026-11-07T23:35:56+00:00 | unknown-route-404-test | 0 | 1.41 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_selection_raises_not_found_for_unknown_cargo` | `a558b8376cd28466` |  |  |
| 2026-11-07T23:37:02+00:00 | mutation-changed-after-404-test | 1 | 61.99 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `6587d75718117f99` | afs-mutation: FAILED score=0.790 threshold=0.8 killed=49 survived=13 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.790 threshold=0.8 killed=49 survived=13 files=1 base=origin/main |
| 2026-11-21T20:33:14+00:00 | mutation-first | 0 | 0.33 | `python .migration/harness/tools/afs-mutation` | `5e320471a53c927f` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=bfb9f9f88dcd14e48cb31f15c0338906e333106d |
| 2026-11-21T20:35:17+00:00 | no-candidate-focused | 0 | 4.26 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `bfd430d75cb520a1` |  |  |
| 2026-11-21T20:40:23+00:00 | mutation-changed | 0 | 302.83 | `python .migration/harness/tools/afs-mutation` | `6e67bdd11e502fad` |  | gate=mutation score=0.836 threshold=0.8 killed=51 survived=10 files=1 base=bfb9f9f88dcd14e48cb31f15c0338906e333106d |
| 2026-11-21T20:41:21+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:41:24+00:00 | build-django-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T20:41:26+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:41:28+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T20:41:30+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T20:41:33+00:00 | idiom-ui | 0 | 0.65 | `python .migration/harness/tools/check_ui.py` | `81759ea7845298ef` |  | gate=ui scope="templates changed since bfb9f9f88dcd14e48cb31f15c0338906e333106d" templates=0 findings=0 |
| 2026-11-21T20:42:35+00:00 | regression | 0 | 59.19 | `pytest -q` | `3418786a785c4155` |  |  |
| 2026-11-21T20:43:35+00:00 | crap-coverage | 0 | 57.46 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `1afa7e698806569d` |  |  |
| 2026-11-21T20:43:37+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:43:40+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `4877eadf5e45905d` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-21T20:44:38+00:00 | guidance-mutant-probe | 0 | 1.93 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_explain_when_no_candidates_satisfy_the_deadline` | `bda5018250507163` |  |  |
| 2026-11-21T20:45:20+00:00 | guidance-mutant-assertion | 0 | 2.0 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_explain_when_no_candidates_satisfy_the_deadline` | `c6463504572ea4f5` |  |  |
| 2026-11-21T20:45:40+00:00 | guidance-assertion-red | 1 | 2.03 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_explain_when_no_candidates_satisfy_the_deadline` | `bf41f2e8c34eee5a` | assert route_response.status_code == 200 |  |
| 2026-11-21T20:45:48+00:00 | guidance-assertion-green | 0 | 1.94 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_explain_when_no_candidates_satisfy_the_deadline` | `1c6b0233fa8cd732` |  |  |
| 2026-11-21T20:50:34+00:00 | mutation-changed-final | 0 | 283.37 | `python .migration/harness/tools/afs-mutation` | `f4330488feec1e95` |  | gate=mutation score=0.869 threshold=0.8 killed=53 survived=8 files=1 base=bfb9f9f88dcd14e48cb31f15c0338906e333106d |
| 2026-11-21T20:50:47+00:00 | build-compile-final | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:50:50+00:00 | build-django-check-final | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T20:50:52+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:50:54+00:00 | idiom-ruff-format-final | 1 | 0.01 | `ruff format --check` | `178e1fb65966138a` |  |  |
| 2026-11-21T20:51:02+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T20:51:04+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:51:07+00:00 | idiom-layers-final | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T20:51:10+00:00 | idiom-ui-final | 0 | 0.66 | `python .migration/harness/tools/check_ui.py` | `81759ea7845298ef` |  | gate=ui scope="templates changed since bfb9f9f88dcd14e48cb31f15c0338906e333106d" templates=0 findings=0 |
| 2026-11-21T20:52:13+00:00 | regression-final | 0 | 59.66 | `pytest -q` | `ae20424705c902ae` |  |  |
| 2026-11-21T20:53:25+00:00 | crap-coverage-final | 0 | 69.69 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `7f0047f9043cd12c` |  |  |
| 2026-11-21T20:53:28+00:00 | crap-lizard-final | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:53:31+00:00 | crap-score-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `4877eadf5e45905d` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-21T20:58:19+00:00 | mutation-changed-final | 0 | 285.08 | `python .migration/harness/tools/afs-mutation` | `f4330488feec1e95` |  | gate=mutation score=0.869 threshold=0.8 killed=53 survived=8 files=1 base=bfb9f9f88dcd14e48cb31f15c0338906e333106d |
