# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:06:19+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:10:16+00:00 | behavior-red | 2 | 2.55 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c31cbd21411297e4` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T03:11:39+00:00 | behavior-dialogs | 1 | 4.19 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `109e47ab0f3b87b8` | assert first.status_code == 200 |  |
| 2026-11-18T03:11:50+00:00 | behavior-dialogs | 0 | 3.85 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `0d408efeeb7bde02` |  |  |
| 2026-11-18T03:12:31+00:00 | behavior-dialogs | 0 | 3.94 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `c4fbd302596c4753` |  |  |
| 2026-11-18T03:13:14+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:13:15+00:00 | build-django-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T03:13:18+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:13:19+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `fddb23c4af603d2c` | 148 \|     assert updated.route_specification.destination == cargo.route_specification.destination |  |
| 2026-11-18T03:13:27+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T03:13:28+00:00 | idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T03:13:28+00:00 | idiom-ui | 1 | 0.38 | `python .migration/harness/tools/check_ui.py` | `002b7d579706a9d6` | templates/booking/dashboard/not_routed_table.html:34: sends an htmx request ('hx-get'), but nothing handles error respon | gate=ui scope="templates changed since 2dbd64cba4409e8976ce92a552eacc0b1ca691f7" templates=3 findings=3 |
| 2026-11-18T03:13:54+00:00 | idiom-ui | 0 | 0.37 | `python .migration/harness/tools/check_ui.py` | `aadbbce4119de209` |  | gate=ui scope="templates changed since 2dbd64cba4409e8976ce92a552eacc0b1ca691f7" templates=3 findings=0 |
| 2026-11-18T03:14:02+00:00 | behavior-dialogs | 0 | 3.92 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `60003b6674c06832` |  |  |
| 2026-11-18T03:14:02+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:14:02+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T03:14:03+00:00 | idiom-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T03:15:50+00:00 | behavior-full | 0 | 52.98 | `pytest -q` | `ed89ef9b04730f70` |  |  |
| 2026-11-18T03:16:39+00:00 | crap-coverage | 0 | 44.54 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `9aa8789641221ed2` |  |  |
| 2026-11-18T03:16:40+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:16:40+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `5a19487e0075bb27` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
| 2026-11-18T03:18:42+00:00 | mutation-changed | 1 | 118.66 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `2e0099601a50eae7` | afs-mutation: FAILED score=0.696 threshold=0.8 killed=48 survived=21 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.696 threshold=0.8 killed=48 survived=21 files=1 base=origin/main |
| 2026-11-18T03:19:26+00:00 | behavior-dialogs | 1 | 4.37 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `a7314727cab67a53` | assert response.status_code == 404 |  |
| 2026-11-18T03:19:44+00:00 | behavior-dialogs | 0 | 4.27 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `d3feb6705a67e216` |  |  |
| 2026-11-18T03:21:42+00:00 | mutation-changed | 0 | 112.27 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `7fa0afcd0b71efab` |  | gate=mutation score=0.909 threshold=0.8 killed=60 survived=6 files=1 base=origin/main |
| 2026-11-18T03:22:37+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:22:37+00:00 | build-django-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T03:22:38+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:22:38+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T03:22:38+00:00 | idiom-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T03:22:38+00:00 | idiom-ui | 0 | 0.37 | `python .migration/harness/tools/check_ui.py` | `aadbbce4119de209` |  | gate=ui scope="templates changed since 2dbd64cba4409e8976ce92a552eacc0b1ca691f7" templates=3 findings=0 |
| 2026-11-18T03:23:24+00:00 | behavior-full | 0 | 45.89 | `pytest -q` | `1176481c0af33b30` |  |  |
| 2026-11-18T03:24:15+00:00 | crap-coverage | 0 | 44.05 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `9f5800dbee42ed14` |  |  |
| 2026-11-18T03:24:15+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:24:15+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `ada33f6664bb4357` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
| 2026-11-18T03:27:22+00:00 | mutation-changed | 0 | 111.89 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `7fa0afcd0b71efab` |  | gate=mutation score=0.909 threshold=0.8 killed=60 survived=6 files=1 base=origin/main |
| 2026-11-18T03:28:40+00:00 | behavior-nojs-red | 1 | 4.33 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a96224cff95ec862` | assert response.status_code == 200 |  |
| 2026-11-18T03:29:08+00:00 | idiom-python-fallback | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:29:08+00:00 | idiom-format-fallback | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T03:29:08+00:00 | idiom-ui-fallback | 0 | 0.44 | `python .migration/harness/tools/check_ui.py` | `a714778f54361a26` |  | gate=ui scope="templates changed since 2dbd64cba4409e8976ce92a552eacc0b1ca691f7" templates=4 findings=0 |
| 2026-11-18T03:29:13+00:00 | behavior-dialogs-fallback | 0 | 4.78 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `fed78431c31bb453` |  |  |
| 2026-11-18T03:29:21+00:00 | build-compile-fallback | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:29:21+00:00 | idiom-format-fallback-final | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T03:29:21+00:00 | idiom-ruff-fallback | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:29:21+00:00 | idiom-layers-fallback | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T03:29:21+00:00 | build-django-check-fallback | 0 | 0.33 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T03:30:31+00:00 | behavior-full-fallback | 0 | 44.88 | `pytest -q` | `c5eb6ac8a3b49f70` |  |  |
| 2026-11-18T03:31:19+00:00 | crap-coverage-final | 0 | 43.93 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `5ebd58ae528e4b3c` |  |  |
| 2026-11-18T03:31:22+00:00 | crap-lizard-final | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:31:22+00:00 | crap-score-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `3f312c166bbf236c` |  | gate=crap max=26.0 threshold=30 over=0 methods=209 |
| 2026-11-18T03:33:55+00:00 | mutation-changed-fallback | 0 | 150.29 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `dd48af6b78d5b7ad` |  | gate=mutation score=0.852 threshold=0.8 killed=69 survived=12 files=1 base=origin/main |
| 2026-11-18T03:37:44+00:00 | migration-validate-final | 0 | 4.01 | `python .migration/harness/tools/validate.py .migration` | `a3cead9cf227b8af` |  |  |
