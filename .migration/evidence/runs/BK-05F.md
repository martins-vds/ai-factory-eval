# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T18:52:50+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T18:59:06+00:00 | behavior-red | 2 | 2.74 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `a1f56ea0cf988b91` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-21T19:00:13+00:00 | behavior-green | 1 | 1.54 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `8bb6903f36d8beca` | E       NameError: name 'DjangoCargoRepository' is not defined |  |
| 2026-11-21T19:00:24+00:00 | behavior-green-2 | 1 | 1.7 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `daaff3ace1c19e55` | assert route_response.status_code == 200 |  |
| 2026-11-21T19:00:34+00:00 | behavior-green-3 | 0 | 1.65 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `9bed9041f3a97041` |  |  |
| 2026-11-21T19:00:51+00:00 | lint-focused | 1 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `442d6ffc5b5b97b5` |  |  |
| 2026-11-21T19:01:10+00:00 | lint-details | 1 | 0.01 | `ruff check --output-format concise src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `47778d01717857fb` |  |  |
| 2026-11-21T19:01:36+00:00 | behavior-green-final | 0 | 1.68 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `8ef3627370199135` |  |  |
| 2026-11-21T19:01:39+00:00 | lint-focused-final | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:01:49+00:00 | format-focused | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-21T19:01:53+00:00 | ui-focused | 1 | 0.41 | `python .migration/harness/tools/check_ui.py --all` | `7bd7afd4e4c90bd7` | templates/admin/live_map.html:34: sends an htmx request ('hx-get'), but nothing handles error responses: htmx swaps no 4 | gate=ui scope="every template" templates=20 findings=3 |
| 2026-11-21T19:05:03+00:00 | behavior-edge-cases | 0 | 1.84 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `f30da780d3c971fc` |  |  |
| 2026-11-21T19:05:26+00:00 | lint-edge-final | 1 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `4498a45a1c93b472` | Found 1 error. |  |
| 2026-11-21T19:05:32+00:00 | lint-edge-final-2 | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:05:35+00:00 | format-edge-final | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-21T19:05:37+00:00 | ui-changed-final | 0 | 0.42 | `python .migration/harness/tools/check_ui.py --changed-since 1d9da909` | `7123d121e6fe05b7` |  | gate=ui scope="templates changed since 1d9da909" templates=4 findings=0 |
| 2026-11-21T19:06:18+00:00 | migration-state-validation | 0 | 4.32 | `python .migration/harness/tools/validate.py .migration` | `6fb607b073658220` |  |  |
