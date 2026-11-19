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

## Handoff — afs-migrator · 2026-11-19T00:02:00Z
**State:** blocked  ·  **Branch / PR:** martins-vds/ai-factory-pilot-target#502  ·  **Last commit:** 4a0a975
### Done
- Operator ruling 1 applied: the live-map marker element sets `hx-on::before-swap` to suppress error responses, with a template comment citing `.migration/design/admin-live-map.md`, “Empty and failure behavior.”
- The map test now asserts the per-element opt-out instead of expecting a 500 body to swap.
- Focused tracking/map tests passed (26): `.migration/runs/BK-05K/20261119T000001286284Z-focused-ruling-final.log`.
- All-template UI check passed (21 templates, 0 findings): `.migration/runs/BK-05K/20261119T000001245849Z-ui-all-ruling-final.log`.
- Ruff and format checks passed: `.migration/runs/BK-05K/20261119T000001274279Z-lint-ruling-final.log`.
- A real Playwright browser session loaded htmx 2.0.11 from the CDN, submitted `UNKNOWN`, and showed “Cargo with tracking ID UNKNOWN not found.” in `#tracking-result`.
- Added the npm `htmx.org@2.0.11` minified asset at `tests/fixtures/htmx-2.0.11.min.js`; the advisory database reported no vulnerabilities.
- Cleaned the seed rows created for manual browser verification and stopped the development server.
### Remaining
- [ ] Add a committed Playwright test using `page.route` to route the CDN URL to the pinned fixture.
- [ ] Obtain scope authorization to add the missing Playwright dev dependency in `requirements-dev.txt` (and decide the supported browser installation path); Playwright is not currently installed or declared in the repository.
- [ ] After authorization, add/run the browser test, update this return/evidence, run the required gates, and complete finish validation.
### Decisions made
- The operator ruling resolves the map behavior conflict: live-map query errors remain silent; other pages keep global htmx error swapping.
### Blockers / questions
- The operator’s AFS-SCOPE extension names only `tests/fixtures/htmx-2.0.11.min.js`. A reproducible Playwright test requires a Playwright package and browser runtime, neither present in `requirements-dev.txt` or the test environment. Do not edit the dependency manifest without scope authorization.
### Failing commands
- None. One intermediate lint/format run failed only because Ruff requested formatting; the test was formatted and the final check passed.
### Next step for the next session
Ask the operator to authorize the required Playwright test dependency/browser setup file(s), then add the browser regression test and route the htmx CDN URL to the fixture with `page.route`.
