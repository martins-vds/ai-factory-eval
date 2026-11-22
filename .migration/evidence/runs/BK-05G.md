# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:40:11+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:43:48+00:00 | dialogs-red | 2 | 3.06 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `d40dbd9c677d6847` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-22T17:44:58+00:00 | dialogs-targeted | 1 | 4.48 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `30260f25f044a078` | assert cargo is not None |  |
| 2026-11-22T17:45:15+00:00 | dialogs-targeted | 0 | 4.22 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `dc7e08367c35089d` |  |  |
| 2026-11-22T17:46:20+00:00 | dialogs-targeted | 0 | 4.93 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `aae4acc193d409eb` |  |  |
| 2026-11-22T17:47:10+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:47:14+00:00 | build-check | 0 | 0.34 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T17:47:17+00:00 | idiom-ruff | 1 | 0.02 | `ruff check` | `cd323d79091dbc04` | Found 1 error. |  |
| 2026-11-22T17:47:24+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T17:47:27+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `e4373f1e62cf038b` | 50 \| def _deadline_context(cargo: Cargo, value: str = '', error: str = '') -> dict[str, object]: |  |
| 2026-11-22T17:47:32+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-22T17:47:35+00:00 | idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-22T17:47:39+00:00 | idiom-ui | 0 | 0.55 | `python .migration/harness/tools/check_ui.py` | `155001eb467e1b84` |  | gate=ui scope="templates changed since a5a2fdf4f0431a1e6fbf29dcbda1a9df126efa17" templates=4 findings=0 |
