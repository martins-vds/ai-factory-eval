# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:08:44+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:11:59+00:00 | behavior-red | 2 | 3.58 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8b8e9007a23ad6e9` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-21T13:13:28+00:00 | behavior | 1 | 6.3 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `c207e86817c43635` | assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table |  |
| 2026-11-21T13:13:46+00:00 | behavior | 0 | 5.89 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `80e6b1ef218f977a` |  |  |
| 2026-11-21T13:13:50+00:00 | lint | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:13:52+00:00 | format-check | 1 | 0.02 | `ruff format --check` | `a54dc92f2f346e41` |  |  |
| 2026-11-21T13:15:12+00:00 | behavior | 0 | 5.66 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `619fa21779391c4f` |  |  |
| 2026-11-21T13:15:15+00:00 | format-check | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T13:15:27+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:15:30+00:00 | build-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T13:15:32+00:00 | layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T13:15:35+00:00 | ui | 0 | 0.47 | `python .migration/harness/tools/check_ui.py` | `7c6e08b8dc3096de` |  | gate=ui scope="templates changed since b4373fca788d17c369e8b391a410a0bdde2d5765" templates=4 findings=0 |
| 2026-11-21T13:16:13+00:00 | behavior | 0 | 6.06 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `1d67d03e5efe201b` |  |  |
