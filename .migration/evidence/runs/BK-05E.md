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
| 2026-11-16T17:29:10+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:30:34+00:00 | build-compileall | 0 | 0.1 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:30:35+00:00 | build-django-check | 0 | 1.61 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T17:30:35+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T17:30:36+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `b30e83bb722165b1` |  |  |
| 2026-11-16T17:31:38+00:00 | behavior | 0 | 61.99 | `pytest -q` | `68b5e582983b94de` |  |  |
| 2026-11-16T17:32:48+00:00 | regression | 0 | 70.1 | `pytest -q` | `c1f2c2162e60f96b` |  |  |
| 2026-11-16T17:33:44+00:00 | crap-coverage | 0 | 56.04 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `79015a17f67cc452` |  |  |
| 2026-11-16T17:33:44+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:33:44+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
| 2026-11-16T17:42:55+00:00 | mutation-changed | 0 | 550.89 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `99c3c637fc12de56` |  | gate=mutation score=0.919 threshold=0.8 killed=248 survived=22 files=4 base=origin/main |
| 2026-11-16T17:44:18+00:00 | verifier-targeted | 0 | 4.22 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `8ab668493afe54c6` |  |  |
| 2026-11-16T17:44:39+00:00 | build-compileall-final | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:44:40+00:00 | build-django-check-final | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T17:44:40+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T17:44:40+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `b30e83bb722165b1` |  |  |
| 2026-11-16T17:45:35+00:00 | behavior-final | 0 | 55.39 | `pytest -q` | `7c265ab6d81e5509` |  |  |
| 2026-11-16T17:46:33+00:00 | regression-final | 0 | 57.8 | `pytest -q` | `a3e0e444a5fa367f` |  |  |
| 2026-11-16T17:47:30+00:00 | crap-coverage-final | 0 | 56.97 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `7b6698b94fd40116` |  |  |
| 2026-11-16T17:47:30+00:00 | crap-lizard-final | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:47:31+00:00 | crap-score-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
| 2026-11-16T17:57:07+00:00 | mutation-changed-final | 0 | 569.13 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `99c3c637fc12de56` |  | gate=mutation score=0.919 threshold=0.8 killed=248 survived=22 files=4 base=origin/main |
| 2026-11-16T17:59:04+00:00 | verifier-targeted-404 | 0 | 4.26 | `pytest -q tests/booking/interfaces/test_cargo_details.py tests/booking/interfaces/test_dashboard.py` | `dd0a1e4c9fe344e8` |  |  |
| 2026-11-16T17:59:24+00:00 | build-compileall-verified | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:59:25+00:00 | build-django-check-verified | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T17:59:25+00:00 | idiom-ruff-check-verified | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T17:59:25+00:00 | idiom-ruff-format-verified | 0 | 0.01 | `ruff format --check` | `b30e83bb722165b1` |  |  |
| 2026-11-16T18:00:22+00:00 | behavior-verified | 0 | 57.3 | `pytest -q` | `83621ff8db212844` |  |  |
| 2026-11-16T18:01:20+00:00 | regression-verified | 0 | 57.61 | `pytest -q` | `e004f60e072d65f6` |  |  |
| 2026-11-16T18:02:28+00:00 | crap-coverage-verified | 0 | 67.73 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `dd2d5ea06d5a329f` |  |  |
| 2026-11-16T18:02:28+00:00 | crap-lizard-verified | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T18:02:28+00:00 | crap-score-verified | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
