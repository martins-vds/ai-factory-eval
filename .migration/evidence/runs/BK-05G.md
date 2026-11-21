# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:38:11+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:43:13+00:00 | dialogs-red | 2 | 1.33 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `74d2ff40db76c3cc` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-21T22:44:23+00:00 | dialogs-focused | 0 | 4.17 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cb3a674306b64774` |  |  |
| 2026-11-21T22:44:32+00:00 | dashboard-regression | 0 | 5.19 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `1f9aaea92c7f31f6` |  |  |
| 2026-11-21T22:45:45+00:00 | dialogs-e2e | 0 | 5.74 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `35ee3415f353cf4d` |  |  |
| 2026-11-21T22:46:24+00:00 | ruff-check | 1 | 0.02 | `ruff check` | `3bec43a70de0a6b4` | Found 1 error. |  |
| 2026-11-21T22:46:31+00:00 | ruff-fix | 0 | 0.01 | `ruff check --fix tests/booking/interfaces/test_dialogs.py` | `aac3a0503d8b9505` | Found 1 error (1 fixed, 0 remaining). |  |
| 2026-11-21T22:46:35+00:00 | ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T22:46:37+00:00 | ruff-format | 1 | 0.02 | `ruff format --check` | `723e94aa76844915` | 272 \|     assert cargo_after.route_specification.origin == cargo_before.route_specification.origin |  |
| 2026-11-21T22:46:40+00:00 | format-fix | 0 | 0.01 | `ruff format tests/booking/interfaces/test_dialogs.py` | `413a709001976657` |  |  |
| 2026-11-21T22:46:42+00:00 | ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T22:46:52+00:00 | dialogs-e2e | 0 | 5.77 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `96907f08a34afe3d` |  |  |
| 2026-11-21T22:46:54+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:46:57+00:00 | build-django-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T22:46:59+00:00 | layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T22:47:03+00:00 | ui-check | 0 | 0.52 | `python .migration/harness/tools/check_ui.py` | `ed2097a95ff239c0` |  | gate=ui scope="templates changed since b773736ccfce81b6efe150bd40331263565175d5" templates=4 findings=0 |
| 2026-11-21T22:49:01+00:00 | behavior-dialogs | 0 | 4.77 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6887e04acc712e3e` |  |  |
| 2026-11-21T22:49:04+00:00 | build-compileall | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:49:06+00:00 | build-django-check | 0 | 0.34 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T22:49:09+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T22:49:12+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T22:49:14+00:00 | idiom-layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T22:49:17+00:00 | idiom-ui | 0 | 0.53 | `python .migration/harness/tools/check_ui.py` | `ed2097a95ff239c0` |  | gate=ui scope="templates changed since b773736ccfce81b6efe150bd40331263565175d5" templates=4 findings=0 |
| 2026-11-21T22:50:18+00:00 | behavior-suite | 0 | 56.74 | `pytest -q` | `97e47a296994eb42` |  |  |
| 2026-11-21T22:51:16+00:00 | crap-coverage | 0 | 54.39 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `ce81390cb289987e` |  |  |
| 2026-11-21T22:51:19+00:00 | crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:51:23+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `306b1b1e8a677fbd` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-21T22:57:39+00:00 | mutation-changed | 1 | 373.89 | `python .migration/harness/tools/afs-mutation` | `24f25c56047acd0a` | afs-mutation: FAILED score=0.679 threshold=0.8 killed=38 survived=18 skipped=0 files=1 jobs=1 base=b773736ccfce81b6efe15 | gate=mutation score=0.679 threshold=0.8 killed=38 survived=18 files=1 base=b773736ccfce81b6efe150bd40331263565175d5 |
| 2026-11-21T22:58:48+00:00 | mutation-tests-format | 0 | 0.01 | `ruff format src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `43affe539ba0ae8b` |  |  |
| 2026-11-21T22:58:57+00:00 | mutation-tests-focused | 0 | 5.72 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `b62c9c880d86c132` |  |  |
| 2026-11-21T23:01:27+00:00 | mutation-changed | 0 | 144.27 | `python .migration/harness/tools/afs-mutation` | `14e68a076660cf06` |  | gate=mutation score=0.961 threshold=0.8 killed=49 survived=2 files=1 base=b773736ccfce81b6efe150bd40331263565175d5 |
| 2026-11-21T23:02:33+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:02:36+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T23:03:06+00:00 | final-build-compileall | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:03:10+00:00 | final-build-django-check | 0 | 0.34 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T23:03:18+00:00 | final-behavior-dialogs | 0 | 5.53 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ffc4b0afa903101d` |  |  |
| 2026-11-21T23:03:20+00:00 | final-idiom-ruff | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:03:22+00:00 | final-idiom-format | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-21T23:03:29+00:00 | final-idiom-layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T23:03:31+00:00 | final-idiom-ui | 0 | 0.53 | `python .migration/harness/tools/check_ui.py` | `ed2097a95ff239c0` |  | gate=ui scope="templates changed since b773736ccfce81b6efe150bd40331263565175d5" templates=4 findings=0 |
| 2026-11-21T23:04:29+00:00 | final-regression-suite | 0 | 55.61 | `pytest -q` | `4178bd0f26242c7e` |  |  |
| 2026-11-21T23:05:29+00:00 | final-crap-coverage | 0 | 57.64 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `f5154807c84479b3` |  |  |
| 2026-11-21T23:05:31+00:00 | final-crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:05:33+00:00 | final-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `9ed199729e2449b0` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-21T23:08:00+00:00 | final-mutation-changed | 0 | 143.91 | `python .migration/harness/tools/afs-mutation` | `14e68a076660cf06` |  | gate=mutation score=0.961 threshold=0.8 killed=49 survived=2 files=1 base=b773736ccfce81b6efe150bd40331263565175d5 |
| 2026-11-21T23:08:05+00:00 | final-idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:08:08+00:00 | final-idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
