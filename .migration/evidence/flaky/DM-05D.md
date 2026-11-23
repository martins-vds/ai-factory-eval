# Flaky runs: DM-05D

Written by afs-run (ADR-0070): each section is a gate command that failed and then passed on the same code. Commit this file; the afs-flaky workflow opens a ticket for each test.

## `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml`
- failed: 2026-11-23T00:59:41+00:00 (exit 1, log `.migration/runs/DM-05D/20261123T005941023140Z-data-load-check.log`)
- passed: 2026-11-23T00:59:55+00:00, same code (tree `c1cba79d2d44`)
- tests that failed: none named in the log
