# Run journal: BK-05E

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T18:23:06+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T18:27:09+00:00 | tests-red | 2 | 2.95 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `5919781dca1433e6` | _________ ERROR collecting tests/booking/interfaces/test_dashboard.py __________ |  |
| 2026-11-07T18:28:12+00:00 | tests-targeted | 0 | 2.94 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `d45996ff8b3a07ca` |  |  |
| 2026-11-07T18:28:43+00:00 | tests-targeted | 0 | 2.84 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `bf97953a21a0c167` |  |  |
| 2026-11-07T18:29:05+00:00 | build-compileall | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T18:29:05+00:00 | build-django-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-07T18:29:08+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-07T18:29:08+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `f7623b4d5336db55` | 77 \|     assert response.status_code == 200 |  |
| 2026-11-07T18:29:13+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `c7a0bcb17dd5241a` |  |  |
| 2026-11-07T18:30:01+00:00 | tests | 0 | 44.68 | `pytest -q` | `fde32fcce61583e5` |  |  |
| 2026-11-07T18:30:44+00:00 | crap-coverage | 0 | 37.61 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `ff6e6eba749aaa31` |  |  |
| 2026-11-07T18:30:44+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T18:30:44+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `efcf0c40f9c44d17` |  | gate=crap max=26.0 threshold=30 over=0 methods=180 |
| 2026-11-07T18:31:15+00:00 | mutation-changed | 0 | 25.98 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `4e8520baafe17cc5` |  | gate=mutation score=0.929 threshold=0.8 killed=13 survived=1 files=1 base=origin/main |
| 2026-11-15T04:10:31+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T04:17:23+00:00 | verifier-focused-tests | 1 | 7.32 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `bd9757b2c908ad60` | E       NameError: name 'TrackingId' is not defined |  |
| 2026-11-15T04:17:39+00:00 | verifier-focused-tests | 0 | 4.76 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `4b2aac9c61149332` |  |  |
| 2026-11-15T04:18:01+00:00 | verifier-final-build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T04:18:05+00:00 | verifier-final-build-django-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T04:19:10+00:00 | verifier-final-behavior-tests | 0 | 60.98 | `pytest -q` | `efa121283ccc5eeb` |  |  |
| 2026-11-15T04:19:15+00:00 | verifier-final-idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T04:19:15+00:00 | verifier-final-idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `df313bb2dd82ede5` |  |  |
| 2026-11-15T04:20:31+00:00 | verifier-final-crap-coverage | 0 | 70.57 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `f7a7b54d1e69800d` |  |  |
| 2026-11-15T04:20:35+00:00 | verifier-final-crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T04:20:38+00:00 | verifier-final-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
| 2026-11-15T04:46:48+00:00 | verifier-final-detail-branches | 0 | 4.82 | `pytest -q tests/booking/interfaces/test_cargo_details.py tests/booking/interfaces/test_dashboard.py` | `cd9c342e604a3cfd` |  |  |
| 2026-11-15T04:48:04+00:00 | verifier-final-regression | 0 | 70.79 | `pytest -q` | `83be8426c131127c` |  |  |
| 2026-11-15T04:49:13+00:00 | verifier-final-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T04:49:13+00:00 | verifier-final-format | 0 | 0.01 | `ruff format --check` | `df313bb2dd82ede5` |  |  |
