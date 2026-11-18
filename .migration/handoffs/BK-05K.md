## Handoff — afs-migrator · 2026-11-18T22:42:00Z
**State:** needs human  ·  **Branch / PR:** martins-vds/ai-factory-pilot-target#502  ·  **Last commit:** f9ffec3
### Done
- Implemented the shared htmx 2 response handling and affected page targets; six page tests are in `tests/test_htmx_errors.py`.
- Fresh UI check passed: 21 templates, 0 findings; see `.migration/runs/BK-05K/20261118T223919960821Z-verification-ui-all.log`.
- Fresh regression suite passed: 530 tests; see `.migration/runs/BK-05K/20261118T223923086884Z-verification-regression.log`.
- All profile gates passed, with CRAP 26.0 and mutation `n/a: no mutable code changed`; see `.migration/evidence/runs/BK-05K.md`.
- CodeQL found 0 alerts. The independent standards review found no issues.
### Remaining
- [ ] Get a human ruling on whether BK-05K supersedes the approved live-map failure decision.
- [ ] Resolve the spec review question about whether generic 404/500 bodies adequately prove that the intended error fragment is swapped.
- [ ] After the ruling, update implementation/tests or the design decision as directed, then rerun the affected gates and finish validation.
### Decisions made
- No product behavior decision made. The current implementation follows BK-05K, pending human ruling.
### Blockers / questions
- `.migration/design/admin-live-map.md` requires network/server cargo-query failures to show no user-facing error message; BK-05K explicitly requires failed live-map htmx responses to render. The spec review found no explicit ruling that supersedes the earlier design. A human must decide which behavior is authoritative.
- The spec review also noted the 404/500 tests assert generic Django error text and check the page target separately; confirm whether this is sufficient evidence for “assert fragment in swap target response.”
### Failing commands
- None.
### Next step for the next session
Read this handoff and BK-05K's acceptance criteria, obtain or locate the human ruling on map failure behavior, then continue with the corresponding test and implementation changes.
