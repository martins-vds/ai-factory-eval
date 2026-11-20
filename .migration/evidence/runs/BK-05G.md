# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:34:42+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:38:24+00:00 | dialogs-red-table | 1 | 2.79 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a202bd45c665cac4` | assert cargo is not None |  |
| 2026-11-20T00:38:46+00:00 | dialogs-green-table | 0 | 2.29 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `488b55d0b06d1251` |  |  |
| 2026-11-20T00:40:06+00:00 | dialogs-red-views | 2 | 1.08 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `b57025eeed794451` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-20T00:40:42+00:00 | dialogs-tests | 1 | 2.35 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0760d4a3a2c4c708` | _ ERROR at setup of test_not_routed_table_opens_destination_and_deadline_dialogs _ |  |
| 2026-11-20T00:40:56+00:00 | dialogs-tests | 0 | 6.63 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4aacc64bf85b7490` |  |  |
| 2026-11-20T00:41:10+00:00 | dashboard-regression | 0 | 7.9 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_dialogs.py` | `49bcda0ac892ac1c` |  |  |
| 2026-11-20T00:48:07+00:00 | dialogs-red-no-js | 1 | 7.24 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `f3790d4a842362c0` | assert cargo is not None |  |
| 2026-11-20T00:49:02+00:00 | dialogs-no-js-fallback | 0 | 7.11 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cd7bcc7d41fe3f3b` |  |  |
| 2026-11-20T00:49:14+00:00 | layers-check | 0 | 0.18 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-20T00:49:14+00:00 | ui-check | 0 | 0.73 | `python .migration/harness/tools/check_ui.py` | `16328f442d5b283e` |  | gate=ui scope="templates changed since c6d033992ff59d8640efed62f3b53589e26bd69f" templates=7 findings=0 |
| 2026-11-20T00:49:22+00:00 | focused-regression-final | 0 | 8.22 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_dialogs.py` | `c2150a10910a5d4f` |  |  |
| 2026-11-20T00:49:28+00:00 | ruff-format | 1 | 0.04 | `ruff format --check` | `2191be9d8cde1cf8` |  |  |
| 2026-11-20T00:49:28+00:00 | ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:49:38+00:00 | ruff-format | 0 | 0.03 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T00:49:46+00:00 | focused-regression-current | 0 | 8.13 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_dialogs.py` | `787245bc802e85eb` |  |  |
| 2026-11-20T00:50:30+00:00 | ruff-check-current | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:50:30+00:00 | ruff-format-current | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T00:50:38+00:00 | focused-regression-current | 0 | 8.91 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_dialogs.py` | `31076622912c294d` |  |  |
| 2026-11-20T00:51:12+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:51:12+00:00 | build-django-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T00:51:20+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:51:21+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T00:51:21+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-20T00:51:21+00:00 | idiom-ui | 0 | 0.61 | `python .migration/harness/tools/check_ui.py` | `16328f442d5b283e` |  | gate=ui scope="templates changed since c6d033992ff59d8640efed62f3b53589e26bd69f" templates=7 findings=0 |
| 2026-11-20T00:52:32+00:00 | behavior | 0 | 65.71 | `pytest -q` | `9c48208230c4227d` |  |  |
| 2026-11-20T00:53:40+00:00 | crap-coverage | 0 | 62.49 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `ba9de0f3bb1acbde` |  |  |
| 2026-11-20T00:53:41+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:53:41+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `9a9836667161a845` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
| 2026-11-20T01:02:35+00:00 | mutation-changed | 1 | 512.97 | `python .migration/harness/tools/afs-mutation` | `af2872ec85989519` | afs-mutation: FAILED score=0.789 threshold=0.8 killed=56 survived=15 skipped=0 files=1 jobs=1 base=c6d033992ff59d8640efe | gate=mutation score=0.789 threshold=0.8 killed=56 survived=15 files=1 base=c6d033992ff59d8640efed62f3b53589e26bd69f |
| 2026-11-20T01:03:44+00:00 | mutation-tests-ruff | 0 | 0.01 | `ruff check tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T01:03:52+00:00 | mutation-tests-strengthened | 0 | 8.43 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `10a62fd9e6a323f3` |  |  |
| 2026-11-20T01:12:29+00:00 | mutation-changed | 0 | 478.67 | `python .migration/harness/tools/afs-mutation` | `a480e8e29bf7350f` |  | gate=mutation score=0.887 threshold=0.8 killed=63 survived=8 files=1 base=c6d033992ff59d8640efed62f3b53589e26bd69f |
| 2026-11-20T01:13:31+00:00 | final-build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T01:13:31+00:00 | final-build-django-check | 0 | 0.45 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T01:13:31+00:00 | final-idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T01:13:32+00:00 | final-idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T01:13:32+00:00 | final-idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-20T01:13:33+00:00 | final-idiom-ui | 0 | 0.67 | `python .migration/harness/tools/check_ui.py` | `16328f442d5b283e` |  | gate=ui scope="templates changed since c6d033992ff59d8640efed62f3b53589e26bd69f" templates=7 findings=0 |
| 2026-11-20T01:14:59+00:00 | final-behavior | 0 | 76.45 | `pytest -q` | `c9746c66a257fab8` |  |  |
| 2026-11-20T01:16:22+00:00 | final-crap-coverage | 0 | 77.79 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `25a75c3616d063c7` |  |  |
| 2026-11-20T01:16:22+00:00 | final-crap-lizard | 0 | 0.17 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T01:16:22+00:00 | final-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `9a9836667161a845` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
| 2026-11-20T01:17:47+00:00 | final-migration-validation | 2 | 0.14 | `python .migration/harness/tools/validate.py` | `8ccf6c31e456c000` | validate.py: error: the following arguments are required: folder |  |
| 2026-11-20T01:17:55+00:00 | final-migration-validation | 0 | 5.12 | `python .migration/harness/tools/validate.py .migration` | `7c75cd4a68d80691` |  |  |
