# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T00:43:48+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:44:07+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-23T00:45:48+00:00 | export-tests-red | 1 | 1.91 | `pytest -q tests/data_migration/test_export.py` | `092e91a45747a908` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-23T00:46:16+00:00 | export-tests-green | 1 | 1.71 | `pytest -q tests/data_migration/test_export.py` | `050b23fe833b5cb6` | assert reconciliation.returncode == 0, reconciliation.stdout + reconciliation.stderr |  |
| 2026-11-23T00:46:23+00:00 | export-tests-green | 0 | 1.73 | `pytest -q tests/data_migration/test_export.py` | `0dd8334b9d136db6` |  |  |
| 2026-11-23T00:47:00+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:47:01+00:00 | build-django-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T00:47:01+00:00 | lint-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:47:01+00:00 | format-check | 1 | 0.02 | `ruff format --check` | `10fae0c146ce8319` |  |  |
| 2026-11-23T00:47:09+00:00 | format-check | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-23T00:47:09+00:00 | layers-check | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T00:47:09+00:00 | ui-check | 0 | 0.54 | `python .migration/harness/tools/check_ui.py` | `55cb456d902de042` |  | gate=ui scope="templates changed since 81aa20bcdc6acc38608db76d3f20546cefcfbf4c" templates=0 findings=0 |
