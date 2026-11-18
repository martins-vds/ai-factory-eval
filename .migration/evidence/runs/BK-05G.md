# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:50:51+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:53:54+00:00 | tests-red | 2 | 2.54 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ff2941dac61b6088` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:54:46+00:00 | dialogs-targeted | 1 | 6.9 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `a6b0390320c840a7` | assert locations == initial_locations |  |
| 2026-11-18T12:55:07+00:00 | dialogs-targeted | 1 | 6.56 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `ca4bb3ba4a0cb0cd` | assert locations == initial_locations |  |
| 2026-11-18T12:55:23+00:00 | dialogs-targeted | 0 | 6.42 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `a5692a78cfee1117` |  |  |
| 2026-11-18T12:55:50+00:00 | dialogs-targeted | 0 | 6.62 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `2ef850f287531bdb` |  |  |
| 2026-11-18T12:56:24+00:00 | dialogs-targeted | 1 | 6.64 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `3035f919e469ef4e` | /opt/hostedtoolcache/Python/3.13.18/x64/lib/python3.13/site-packages/django/core/handlers/exception.py:55: in inner |  |
| 2026-11-18T12:56:36+00:00 | dialogs-targeted | 0 | 6.85 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `b09713926ed0ac0a` |  |  |
| 2026-11-18T12:56:42+00:00 | build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:56:42+00:00 | build-django-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T12:56:42+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:56:42+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `c82bdde39e998bc0` | 143 \|     assert 'New York' in content |  |
| 2026-11-18T12:56:51+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-18T12:56:55+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:56:56+00:00 | idiom-ui | 1 | 0.54 | `python .migration/harness/tools/check_ui.py` | `65e1f4087b1c7fe4` | templates/booking/dialogs/deadline.html:9: sends an htmx request ('hx-post'), but nothing handles error responses: htmx  | gate=ui scope="templates changed since 07c357cf95f91dfffaf2334a0675068b38745e1d" templates=2 findings=2 |
| 2026-11-18T12:57:22+00:00 | idiom-ui | 0 | 0.51 | `python .migration/harness/tools/check_ui.py` | `8be7bd64cfb1043a` |  | gate=ui scope="templates changed since 07c357cf95f91dfffaf2334a0675068b38745e1d" templates=2 findings=0 |
