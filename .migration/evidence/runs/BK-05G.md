# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:39:43+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:42:57+00:00 | behavior-red | 2 | 2.26 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `f19ca8a18341ed71` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T21:43:38+00:00 | destination-get | 0 | 1.63 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `856d0c92bfd158ae` |  |  |
| 2026-11-19T21:44:13+00:00 | destination-update-red | 1 | 2.0 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `1b4f54d79c95567b` | assert original is not None |  |
| 2026-11-19T21:44:25+00:00 | destination-update | 0 | 1.93 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8178d932945c4da3` |  |  |
| 2026-11-19T21:45:02+00:00 | deadline-parse-red | 2 | 0.86 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0e0e1784a17779b9` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T21:45:20+00:00 | deadline-parse | 0 | 2.19 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cd9450ea88aea29a` |  |  |
| 2026-11-19T21:45:35+00:00 | deadline-update | 0 | 2.44 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6be2b0172056f19b` |  |  |
| 2026-11-19T21:45:53+00:00 | table-dialog-triggers-red | 1 | 2.86 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bc26d81ef35cb87f` | assert cargo is not None |  |
| 2026-11-19T21:46:06+00:00 | table-dialog-triggers | 0 | 2.82 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bf97953a21a0c167` |  |  |
| 2026-11-19T21:46:20+00:00 | destination-stable-options | 0 | 3.22 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0847539c16930f33` |  |  |
| 2026-11-19T21:46:36+00:00 | destination-invalid | 0 | 3.98 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0d408efeeb7bde02` |  |  |
| 2026-11-19T21:46:53+00:00 | unknown-cargo-red | 1 | 4.32 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `d353f42a04fc976d` | E       django.template.exceptions.TemplateDoesNotExist: booking/dialogs/not_found.html |  |
| 2026-11-19T21:47:03+00:00 | unknown-cargo | 0 | 4.08 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `10f427b37861acf3` |  |  |
| 2026-11-19T21:47:34+00:00 | refreshed-dashboard-rows | 0 | 3.89 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `dee9af3eb0ffa744` |  |  |
| 2026-11-19T21:48:16+00:00 | focused-tests | 0 | 4.78 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `0811ce6026dd74b6` |  |  |
| 2026-11-19T21:48:19+00:00 | ui-check | 0 | 0.31 | `python .migration/harness/tools/check_ui.py` | `7a5084a4fa1548c2` |  | gate=ui scope="templates changed since 6348f858891024d9bfc2ae05d30336a1bf9f2a12" templates=3 findings=0 |
| 2026-11-19T21:48:24+00:00 | ruff-check | 1 | 0.02 | `ruff check` | `38b83a01dda096cc` | Found 1 error. |  |
| 2026-11-19T21:48:34+00:00 | ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:48:34+00:00 | ruff-format | 1 | 0.02 | `ruff format --check` | `07b1e3c185322f85` | 149 \|     assert updated.route_specification.destination.unlocode.value == 'USNYC' |  |
| 2026-11-19T21:48:43+00:00 | ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:48:43+00:00 | ruff-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T21:48:48+00:00 | focused-tests-final | 0 | 4.71 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `e793184a9d9ec9bf` |  |  |
| 2026-11-19T21:51:17+00:00 | build-compileall | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:51:30+00:00 | build-check | 0 | 0.32 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T21:52:16+00:00 | behavior | 0 | 42.52 | `pytest -q` | `68db49dec42edf2c` |  |  |
| 2026-11-19T21:52:23+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:52:26+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T21:52:30+00:00 | idiom-layers | 0 | 0.1 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T21:52:34+00:00 | idiom-ui | 0 | 0.34 | `python .migration/harness/tools/check_ui.py` | `48f6c439f84cbf94` |  | gate=ui scope="templates changed since 6348f858891024d9bfc2ae05d30336a1bf9f2a12" templates=4 findings=0 |
| 2026-11-19T21:53:24+00:00 | crap-coverage | 0 | 38.25 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov'` | `e37d877fcdd0a2cd` |  |  |
| 2026-11-19T21:53:27+00:00 | crap-lizard | 0 | 0.1 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:53:30+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `9fce652a573cddd2` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-19T21:55:44+00:00 | mutation-changed | 1 | 119.08 | `python .migration/harness/tools/afs-mutation` | `5cfa1cb72894f40a` | afs-mutation: FAILED score=0.750 threshold=0.8 killed=42 survived=14 skipped=0 files=1 jobs=1 base=6348f858891024d9bfc2a | gate=mutation score=0.750 threshold=0.8 killed=42 survived=14 files=1 base=6348f858891024d9bfc2ae05d30336a1bf9f2a12 |
| 2026-11-19T21:57:58+00:00 | mutation-gap-tests | 0 | 3.98 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0621494a41d3bffa` |  |  |
| 2026-11-19T21:58:20+00:00 | mutation-gap-green | 0 | 4.43 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `2fdc990df5d2bccf` |  |  |
| 2026-11-19T21:58:25+00:00 | mutation-gap-lint | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:58:25+00:00 | mutation-gap-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T22:01:06+00:00 | mutation-changed-final | 0 | 98.26 | `python .migration/harness/tools/afs-mutation` | `be77d2961761ed55` |  | gate=mutation score=0.925 threshold=0.8 killed=49 survived=4 files=1 base=6348f858891024d9bfc2ae05d30336a1bf9f2a12 |
| 2026-11-19T22:01:43+00:00 | final-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T22:01:43+00:00 | final-build-django | 0 | 0.33 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T22:01:51+00:00 | final-focused-behavior | 0 | 5.06 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `6808687b68dd31dd` |  |  |
| 2026-11-19T22:01:55+00:00 | final-idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T22:01:55+00:00 | final-idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T22:01:55+00:00 | final-idiom-layers | 0 | 0.1 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T22:01:55+00:00 | final-idiom-ui | 0 | 0.36 | `python .migration/harness/tools/check_ui.py` | `48f6c439f84cbf94` |  | gate=ui scope="templates changed since 6348f858891024d9bfc2ae05d30336a1bf9f2a12" templates=4 findings=0 |
| 2026-11-19T22:02:41+00:00 | final-crap-coverage | 0 | 39.85 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov'` | `af0a5e75cc1b7c68` |  |  |
| 2026-11-19T22:02:41+00:00 | final-crap-lizard | 0 | 0.1 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T22:02:41+00:00 | final-crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `9f969d626564cc0f` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-19T22:03:35+00:00 | final-regression | 0 | 38.13 | `pytest -q` | `908551f50779be54` |  |  |
