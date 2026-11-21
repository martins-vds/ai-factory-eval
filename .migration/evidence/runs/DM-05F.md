# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T22:34:46+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:37:22+00:00 | invariants | 1 | 4.3 | `pytest -q tests/data_migration/test_invariants.py` | `0b6788c4ee094105` | E           ValueError: Voyage is not allowed with event type RECEIVE |  |
| 2026-11-21T22:37:32+00:00 | invariants | 1 | 2.13 | `pytest -q tests/data_migration/test_invariants.py` | `783450f8ed7e5fcc` | >           assert cargo.delivery == replace(derived, last_event_id=history.most_recent_event_id) |  |
| 2026-11-21T22:37:46+00:00 | invariants | 0 | 2.12 | `pytest -q tests/data_migration/test_invariants.py` | `10e96b85b3bd96cf` |  |  |
| 2026-11-21T22:38:14+00:00 | compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:38:15+00:00 | django-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T22:38:18+00:00 | ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T22:38:18+00:00 | ruff-format | 1 | 0.02 | `ruff format --check` | `d085c2c0438a590a` | -         assert ( |  |
| 2026-11-21T22:38:18+00:00 | check-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T22:38:19+00:00 | check-ui | 0 | 0.65 | `python .migration/harness/tools/check_ui.py` | `e30f4e3fbbed8ce9` |  | gate=ui scope="templates changed since bb84eec6b5823b0036f79e9f1838e87d7732c896" templates=0 findings=0 |
| 2026-11-21T22:38:24+00:00 | ruff-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-21T22:39:16+00:00 | regression | 0 | 49.3 | `pytest -q` | `88f873dd451737ae` |  |  |
| 2026-11-21T22:40:11+00:00 | crap-coverage | 0 | 50.14 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `a8780c15f0e4a172` |  |  |
| 2026-11-21T22:40:11+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:40:11+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-21T22:40:14+00:00 | mutation-changed | 0 | 0.1 | `python .migration/harness/tools/afs-mutation` | `2b254c903b8b6679` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=bb84eec6b5823b0036f79e9f1838e87d7732c896 |
