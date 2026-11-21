# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T01:10:40+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T01:13:19+00:00 | idiom | 1 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `814c1f6b1952bbcb` | Found 1 error. |  |
| 2026-11-21T01:13:19+00:00 | build | 0 | 0.09 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T01:13:20+00:00 | behavior | 0 | 1.6 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `68a7542f3ebd7065` |  |  |
| 2026-11-21T01:13:27+00:00 | idiom | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `112163b1d7adce1e` |  |  |
| 2026-11-21T01:13:27+00:00 | idiom | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T01:13:28+00:00 | build | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T01:13:36+00:00 | idiom | 0 | 0.08 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T01:13:36+00:00 | idiom | 0 | 0.07 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T01:13:36+00:00 | idiom | 0 | 0.31 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T01:13:37+00:00 | idiom | 0 | 0.67 | `python .migration/harness/tools/check_ui.py` | `c75e54c263466719` |  | gate=ui scope="templates changed since 3ef02a70b0e74c04018a87fea0aec3e1a8f1edf8" templates=2 findings=0 |
| 2026-11-21T01:14:37+00:00 | behavior | 0 | 61.49 | `pytest -q` | `299a829100bdaaca` |  |  |
| 2026-11-21T01:15:43+00:00 | crap | 0 | 59.23 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `13dc1c14b4ed0a2d` |  |  |
| 2026-11-21T01:15:43+00:00 | crap | 0 | 0.16 | `lizard --csv src` | `d19f0238412a9f5a` | 16,3,86,6,16,"_origin_step@38-53@src/cargotracker/booking/interfaces/wizard/views.py","src/cargotracker/booking/interfac |  |
| 2026-11-21T01:15:43+00:00 | crap | 1 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `1f315dff0c7b9238` |  |  |
| 2026-11-21T01:15:48+00:00 | crap | 0 | 0.38 | `bash -lc 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T01:15:48+00:00 | crap | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `6a28227edb962864` |  | gate=crap max=26.0 threshold=30 over=0 methods=203 |
| 2026-11-21T01:21:10+00:00 | mutation_changed | 1 | 317.13 | `python .migration/harness/tools/afs-mutation` | `e9609ea19b7eea44` | afs-mutation: FAILED score=0.581 threshold=0.8 killed=18 survived=13 skipped=0 files=1 jobs=1 base=3ef02a70b0e74c04018a8 | gate=mutation score=0.581 threshold=0.8 killed=18 survived=13 files=1 base=3ef02a70b0e74c04018a87fea0aec3e1a8f1edf8 |
| 2026-11-21T01:26:55+00:00 | mutation_changed | 0 | 316.45 | `python .migration/harness/tools/afs-mutation` | `1aa8aed59d7b24ff` |  | gate=mutation score=0.839 threshold=0.8 killed=26 survived=5 files=1 base=3ef02a70b0e74c04018a87fea0aec3e1a8f1edf8 |
