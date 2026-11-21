# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T01:09:21+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T01:10:27+00:00 | route-selection-red | 2 | 2.76 | `rtk pytest -q tests/booking/interfaces/test_route_selection.py` | `9bfb4a900cb1a607` | 1. [ERROR] collecting tests/booking/interfaces/test_route_selection.py |  |
| 2026-11-21T01:10:56+00:00 | route-selection-targeted | 1 | 2.64 | `rtk pytest -q tests/booking/interfaces/test_route_selection.py` | `b99c06189aee603b` | Pytest: 0 passed, 3 failed in 2.04s |  |
| 2026-11-21T01:11:21+00:00 | route-selection-targeted | 0 | 2.47 | `rtk pytest -q tests/booking/interfaces/test_route_selection.py` | `4ce02b9f3b76d172` |  |  |
| 2026-11-21T01:12:04+00:00 | route-selection-targeted | 0 | 2.5 | `rtk pytest -q tests/booking/interfaces/test_route_selection.py` | `4e51e42eaa21232b` |  |  |
| 2026-11-21T01:12:09+00:00 | build | 0 | 0.09 | `rtk python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T01:12:09+00:00 | idiom | 1 | 0.28 | `rtk bash -lc 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `7531dca9025de999` |  |  |
| 2026-11-21T01:12:57+00:00 | behavior | 0 | 48.2 | `rtk pytest -q` | `1ebc8f9ce930c169` |  |  |
| 2026-11-21T01:13:04+00:00 | idiom | 0 | 0.8 | `rtk bash -lc 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `500e66fca550d402` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=ui scope="templates changed since b9e468fb6683d78aed40e0cfcfc50bc216e9812d" templates=2 findings=0 |
| 2026-11-21T01:13:55+00:00 | crap | 0 | 51.8 | `rtk bash -lc 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `655336ddb88af95f` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-21T01:17:35+00:00 | mutation_changed | 1 | 272.11 | `rtk python .migration/harness/tools/afs-mutation` | `d71fa7191c44db41` | afs-mutation: FAILED score=0.452 threshold=0.8 killed=19 survived=23 skipped=0 files=1 jobs=1 base=b9e468fb6683d78aed40e | gate=mutation score=0.452 threshold=0.8 killed=19 survived=23 files=1 base=b9e468fb6683d78aed40e0cfcfc50bc216e9812d |
| 2026-11-21T01:18:03+00:00 | route-selection-strengthened | 0 | 3.0 | `rtk pytest -q tests/booking/interfaces/test_route_selection.py` | `338c2a5da73acc89` |  |  |
| 2026-11-21T01:18:12+00:00 | idiom | 0 | 1.14 | `rtk bash -lc 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `500e66fca550d402` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=ui scope="templates changed since b9e468fb6683d78aed40e0cfcfc50bc216e9812d" templates=2 findings=0 |
| 2026-11-21T01:19:22+00:00 | behavior | 1 | 71.6 | `rtk pytest -q` | `8893c059c8b396ca` | 1. [ERROR] at setup of test_registration_persists_new_cargo_with_generated_id_and_empty_itinerary |  |
| 2026-11-21T01:19:37+00:00 | mutation_changed | 1 | 86.34 | `rtk python .migration/harness/tools/afs-mutation` | `5aa3030db61655ba` | afs-mutation: FAILED score=0.667 threshold=0.8 killed=28 survived=14 skipped=0 files=1 jobs=1 base=b9e468fb6683d78aed40e | gate=mutation score=0.667 threshold=0.8 killed=28 survived=14 files=1 base=b9e468fb6683d78aed40e0cfcfc50bc216e9812d |
| 2026-11-21T01:20:27+00:00 | behavior | 0 | 45.14 | `rtk pytest -q` | `afa9d5daeb7d938f` |  |  |
| 2026-11-21T01:21:52+00:00 | mutation_changed | 1 | 82.04 | `rtk python .migration/harness/tools/afs-mutation` | `5aa3030db61655ba` | afs-mutation: FAILED score=0.667 threshold=0.8 killed=28 survived=14 skipped=0 files=1 jobs=1 base=b9e468fb6683d78aed40e | gate=mutation score=0.667 threshold=0.8 killed=28 survived=14 files=1 base=b9e468fb6683d78aed40e0cfcfc50bc216e9812d |
| 2026-11-21T01:22:20+00:00 | migration-validation | 1 | 3.55 | `rtk python .migration/harness/tools/validate.py .migration` | `5e9e92c26a2a3511` | 194 file(s) checked, 5 error(s) |  |
| 2026-11-21T01:22:39+00:00 | migration-validation | 1 | 3.53 | `rtk python .migration/harness/tools/validate.py .migration` | `1511a340c9c170a0` | 194 file(s) checked, 1 error(s) |  |
| 2026-11-21T01:24:08+00:00 | mutation_changed | 1 | 82.72 | `python .migration/harness/tools/afs-mutation` | `5aa3030db61655ba` | afs-mutation: FAILED score=0.667 threshold=0.8 killed=28 survived=14 skipped=0 files=1 jobs=1 base=b9e468fb6683d78aed40e | gate=mutation score=0.667 threshold=0.8 killed=28 survived=14 files=1 base=b9e468fb6683d78aed40e0cfcfc50bc216e9812d |
| 2026-11-21T01:24:20+00:00 | migration-validation | 0 | 3.53 | `rtk python .migration/harness/tools/validate.py .migration` | `a3cead9cf227b8af` |  |  |
| 2026-11-21T01:26:09+00:00 | route-selection-security-fix | 0 | 3.01 | `rtk pytest -q tests/booking/interfaces/test_route_selection.py` | `0c72c91ad48b83be` |  |  |
