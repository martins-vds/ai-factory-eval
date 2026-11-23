# Flaky runs: DM-05D

Written by afs-run (ADR-0070): each section is a gate command that failed and then passed on the same code. Commit this file; the afs-flaky workflow opens a ticket for each test.

## `python manage.py load_data_snapshot --snapshot .migration/data/snapshot/ --mapping .migration/data/mapping.yaml`
- failed: 2026-11-23T00:47:31+00:00 (exit 1, log `.migration/runs/DM-05D/20261123T004730564619Z-snapshot-load.log`)
- passed: 2026-11-23T00:47:41+00:00, same code (tree `c1d3c6c467c0`)
- tests that failed: none named in the log

The initial failure was because the target database migrations had not been applied. After
`python manage.py migrate --noinput`, the snapshot load succeeded; this was setup state, not a
nondeterministic application failure.
