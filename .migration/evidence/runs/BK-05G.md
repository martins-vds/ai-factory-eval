# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:40:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:44:18+00:00 | destination-red | 2 | 2.42 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c2db4cbd54279054` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:45:18+00:00 | destination-get | 1 | 1.99 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e8eb035f18689b20` | assert first_response.status_code == 200 |  |
| 2026-11-18T12:45:28+00:00 | destination-get | 1 | 1.84 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a21a7efbf83058ba` | assert first_response.status_code == 200 |  |
| 2026-11-18T12:45:39+00:00 | destination-get | 1 | 1.87 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `00578af47d1c544b` | assert first_response.status_code == 200 |  |
| 2026-11-18T12:45:58+00:00 | destination-get | 1 | 1.84 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6f84d9c19deac764` | assert first_response.status_code == 200 |  |
| 2026-11-18T12:46:06+00:00 | destination-get | 1 | 1.9 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4876e89860e7dfce` | assert first_response.status_code == 200 |  |
| 2026-11-18T12:46:16+00:00 | destination-get | 0 | 1.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `67ecf94f55b8e441` |  |  |
| 2026-11-18T12:46:30+00:00 | deadline-get-red | 1 | 2.18 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4db3cadd25ad7e41` | >       assert response.status_code == 200 |  |
| 2026-11-18T12:46:49+00:00 | deadline-get | 1 | 2.16 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ea5c1d869ea1a692` | assert response.status_code == 200 |  |
| 2026-11-18T12:47:11+00:00 | deadline-get | 1 | 2.21 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `35f1bd9ba15c44a1` | assert response.status_code == 200 |  |
| 2026-11-18T12:47:20+00:00 | deadline-get | 1 | 2.21 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ba52ccc6552999ff` | assert response.status_code == 200 |  |
| 2026-11-18T12:47:32+00:00 | deadline-get | 0 | 2.13 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `825826ec75aed015` |  |  |
| 2026-11-18T12:48:05+00:00 | deadline-error-red | 1 | 2.59 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cffd48ef25b7bcfe` | assert original is not None |  |
| 2026-11-18T12:48:26+00:00 | deadline-error | 0 | 2.48 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cf96176e01db94c8` |  |  |
| 2026-11-18T12:48:43+00:00 | destination-update-red | 1 | 2.93 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6952d4d9dbaf994d` | assert original is not None |  |
| 2026-11-18T12:49:03+00:00 | destination-update | 0 | 2.85 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `b45312b5d3e71208` |  |  |
| 2026-11-18T12:49:19+00:00 | deadline-update | 0 | 3.29 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `90dfd6d8ae1500b9` |  |  |
| 2026-11-18T12:49:48+00:00 | table-dialogs-red | 1 | 3.64 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bc4ff0cd4ba4cf20` | >       assert 'Change destination' in row |  |
| 2026-11-18T12:50:09+00:00 | dialog-actions | 0 | 4.6 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `7fc2ff7391ccd856` |  |  |
| 2026-11-18T12:50:48+00:00 | dialogs-targeted | 0 | 4.71 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `ec40d53ff0784cbc` |  |  |
| 2026-11-18T12:53:02+00:00 | dialogs-e2e | 0 | 5.2 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `bca10ba2928e76e6` |  |  |
| 2026-11-18T12:53:22+00:00 | idiom-lint | 1 | 0.02 | `ruff check` | `3a0380cae9963eb7` | Found 1 error. |  |
| 2026-11-18T12:53:28+00:00 | idiom-lint-fix | 0 | 0.01 | `ruff check --fix tests/booking/interfaces/test_dialogs.py` | `aac3a0503d8b9505` | Found 1 error (1 fixed, 0 remaining). |  |
| 2026-11-18T12:53:28+00:00 | idiom-lint | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:53:31+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `ce5966d89e2db9aa` | 152 \|     assert updated.route_specification.destination.unlocode.value == 'USNYC' |  |
| 2026-11-18T12:53:35+00:00 | idiom-format-fix | 0 | 0.01 | `ruff format tests/booking/interfaces/test_dialogs.py` | `413a709001976657` |  |  |
| 2026-11-18T12:53:35+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T12:54:06+00:00 | dialogs-e2e-final | 0 | 5.52 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `b22f517c8c969fd6` |  |  |
| 2026-11-18T12:54:45+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:54:45+00:00 | build-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T12:55:39+00:00 | behavior | 0 | 48.7 | `pytest -q` | `3af85a8c0b20cebe` |  |  |
| 2026-11-18T12:55:44+00:00 | idiom-lint-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:55:44+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T12:55:44+00:00 | idiom-layers-final | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:55:45+00:00 | idiom-ui-final | 0 | 0.39 | `python .migration/harness/tools/check_ui.py` | `0837bed28b1a91d5` |  | gate=ui scope="templates changed since be9c0c1f1244e171b47b06cf2cdf70cc8a01573c" templates=4 findings=0 |
| 2026-11-18T12:56:40+00:00 | crap-coverage | 0 | 46.88 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `b5463a3c05740af9` |  |  |
| 2026-11-18T12:56:40+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:56:41+00:00 | crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `420541cced10adbe` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-18T12:59:01+00:00 | mutation-changed | 1 | 136.71 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `778644e23e39ede7` | afs-mutation: FAILED score=0.774 threshold=0.8 killed=48 survived=14 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.774 threshold=0.8 killed=48 survived=14 files=1 base=origin/main |
| 2026-11-18T13:00:11+00:00 | dialog-survivor-tests-red | 1 | 6.07 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `b2799b4cec6be536` | assert original is not None |  |
| 2026-11-18T13:00:27+00:00 | dialogs-after-empty-feedback | 0 | 6.05 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `da42493865327e6c` |  |  |
| 2026-11-18T13:03:13+00:00 | mutation-changed | 0 | 142.89 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `e6dc8d62709dfb77` |  | gate=mutation score=0.935 threshold=0.8 killed=58 survived=4 files=1 base=origin/main |
| 2026-11-18T13:04:32+00:00 | regression | 0 | 50.15 | `pytest -q` | `af7303ca9c73ff5c` |  |  |
| 2026-11-18T13:05:08+00:00 | build-compile-final | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:05:09+00:00 | build-check-final | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T13:05:09+00:00 | idiom-lint-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:05:09+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T13:05:09+00:00 | idiom-layers-final | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:05:10+00:00 | idiom-ui-final | 0 | 0.39 | `python .migration/harness/tools/check_ui.py` | `0837bed28b1a91d5` |  | gate=ui scope="templates changed since be9c0c1f1244e171b47b06cf2cdf70cc8a01573c" templates=4 findings=0 |
| 2026-11-18T13:06:05+00:00 | crap-coverage-final | 0 | 47.96 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `50d2cd08cd7e80b7` |  |  |
| 2026-11-18T13:06:05+00:00 | crap-lizard-final | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:06:05+00:00 | crap-threshold-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `1ff736494c69c382` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-18T15:43:12+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
