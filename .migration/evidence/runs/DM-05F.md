# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T01:35:12+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:38:11+00:00 | invariants-tests | 1 | 4.74 | `pytest -q tests/data_migration/test_invariants.py` | `3705e83cb0739c6d` | E           ValueError: Voyage is not allowed with event type RECEIVE |  |
| 2026-11-23T01:38:22+00:00 | invariants-tests | 0 | 2.08 | `pytest -q tests/data_migration/test_invariants.py` | `3c694261c1f3a68b` |  |  |
| 2026-11-23T01:39:15+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:39:18+00:00 | build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T01:39:20+00:00 | idiom-ruff | 1 | 0.02 | `ruff check` | `28ba4536831d5c6e` | 142 \|             assert current.unload_location_id == following.load_location_id |  |
| 2026-11-23T01:39:28+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T01:39:30+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `ef63f0d5d7573ff3` | 129 \|         assert ( |  |
| 2026-11-23T01:39:37+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T01:39:41+00:00 | invariants-tests | 0 | 2.09 | `pytest -q tests/data_migration/test_invariants.py` | `f56eadf3d7746ccb` |  |  |
| 2026-11-23T01:39:44+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T01:39:47+00:00 | idiom-ui | 0 | 0.69 | `python .migration/harness/tools/check_ui.py` | `e4e46c24f598519b` |  | gate=ui scope="templates changed since 1cd03cc02b6a7ff4524cb12d083c3c784c5683f0" templates=0 findings=0 |
| 2026-11-23T01:40:40+00:00 | crap-coverage | 0 | 49.11 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `3a78b4b6878fe6de` |  |  |
| 2026-11-23T01:40:43+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:40:45+00:00 | crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-23T01:40:48+00:00 | mutation-changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation` | `dfd46765a87db804` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=1cd03cc02b6a7ff4524cb12d083c3c784c5683f0 |
| 2026-11-23T01:41:41+00:00 | behavior | 0 | 47.9 | `pytest -q` | `1cc8e8532584ac36` |  |  |
| 2026-11-23T01:41:55+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:41:57+00:00 | build-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T01:44:18+00:00 | regression | 0 | 57.51 | `pytest -q` | `36c2119e7f6d31fe` |  |  |
