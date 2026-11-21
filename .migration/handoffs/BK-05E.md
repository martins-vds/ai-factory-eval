## Handoff — afs-verifier · 2026-11-21T19:11:00Z
**State:** in progress · **Branch / PR:** https://github.com/martins-vds/ai-factory-eval/pull/2083 · **Last commit:** 6df0fca28ec4a0786dd5635aa21466abd14d0d4e

### Done
- Setup passed; source SHA is `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- Dashboard partitions/order, empty tables, fields, links, claimed tooltip, debug-dialog absence, and cargo-details fields were checked against the plan, characterization, and rulings #232, #233, and #237.
- Added passing unrouted and misdirected detail-action tests. The strengthened unknown/stale detail test confirms HTTP 404 but fails because the response omits the approved visible tracking-ID message.
- Build passed; 452 baseline tests passed before verifier assertions. CRAP gate passed at 26.0 (`data_migration.loader._prepare_tables`, 100% line coverage; separate refactor consideration).
- Changed-code mutation passed at 0.919 (248 killed, 22 survived). The BK-05E survivor only alters the `Http404` text; the current generic 404 suppresses that text, though the missing user-visible message is a real contract gap. Most other survivors concern BK-05D wizard behavior or DM-05D exporter behavior.
- `check_layers.py` reports a BK-05E violation: dashboard adapter imports/calls `CargoRepository` directly. `check_ui.py` also reports an inherited BK-05D wizard htmx error-handling issue.

### Remaining
- [ ] A Migrator moves dashboard repository access/partitioning behind an application use case, preserving the verified dashboard behavior.
- [ ] A Migrator renders the approved cargo-not-found message with HTTP 404 for both unknown and stale IDs.
- [ ] Re-run the affected gates and request a fresh Verifier review.

### Decisions made
- Verifier changes are tests and evidence only; production fixes are left to a Migrator.
- No new quirk decision is needed; the applicable #232, #233, and #237 rulings are already approved.

### Blockers / questions
- Production remediation is outside the Verifier role; no unresolved human decision blocks the fixes.

### Failing commands
- `pytest -q tests/booking/interfaces/test_cargo_details.py` → exit 1, see `.migration/runs/BK-05E/20261121T190831558940Z-cargo-details-contract-retry.log:18-22`.
- `python .migration/harness/tools/check_layers.py` → exit 1, see `.migration/runs/BK-05E/20261121T185538650328Z-idiom-layers.log:2-8`.
- `python .migration/harness/tools/check_ui.py` → exit 1, inherited BK-05D issue, see `.migration/runs/BK-05E/20261121T185538858548Z-idiom-ui.log:2-3`.
- `pytest -q` → exit 1 on the required visible 404 message, see `.migration/runs/BK-05E/20261121T191008695191Z-behavior-after-evidence.log:22-28` and `.migration/runs/BK-05E/20261121T191121655231Z-regression-after-evidence.log:22-28`.

### Next step for the next session
Implement the two BK-05E production fixes without weakening these verifier assertions, run the profile gates through `afs-run`, and return for an independent verification.
