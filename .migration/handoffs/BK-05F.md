## Handoff — afs-specialist-migrator · 2026-11-07T23:37:23Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-build-route-selection-itinerary-screens` / https://github.com/martins-vds/ai-factory-pilot-target/pull/394 · **Last commit:** ae812f5

### Done
- Route selection and itinerary screens render cargo details, candidate counts, numbered route/leg data, candidate routes when present, and the characterized empty-state guidance.
- Candidate assignment uses `CargoRouting.assign_route`, verifies the current route specification, and redirects to cargo details. Focused UI tests cover assignment, the redirect/details page, invalid candidate tokens, unsupported methods and unknown cargo.
- The full behavior suite passed with 467 tests (`.migration/runs/BK-05F/20261107T233102987871Z-behavior-security-fix.log`); build, idiom and CRAP gates passed. Migration validation last passed with 193 files and zero errors.
- CodeQL reported `py/url-redirection` at `views.py:38`; the redirect tracking-ID path segment was quoted. The required post-fix CodeQL verification has not yet run.

### Remaining
- [ ] Resolve the changed-code mutation gate shortfall (0.790, minimum 0.8) and rerun the exact profile command.
- [ ] Commit the current redirect-sanitization and test changes, then rerun CodeQL and address any remaining alert.
- [ ] Update the return/evidence with the final mutation result and rerun migration validation.

### Decisions made
- Candidate itineraries are signed in the form so assignment uses the itinerary rendered to the user rather than regenerating randomized candidates on POST.
- The redirect tracking ID is URL-quoted after CodeQL identified it as untrusted redirect data.

### Blockers / questions
- The migration contract stop rule fired after two changed-code mutation attempts reported the same score, 0.790 below the required 0.8. The next session should inspect why the existing interface assertions do not kill the surviving mutants before attempting another run.

### Failing commands
- `python .migration/harness/tools/afs-mutation --changed-since origin/main` → exit 1, see `.migration/runs/BK-05F/20261107T233256117827Z-mutation-changed-security-fix.log`.
- `python .migration/harness/tools/afs-mutation --changed-since origin/main` → exit 1, see `.migration/runs/BK-05F/20261107T233600196049Z-mutation-changed-after-404-test.log`.

### Next step for the next session
Resume BK-05F by reproducing and resolving the mutation-score shortfall first; then commit the pending fix, rerun CodeQL, update the return file, and validate all evidence.

## Handoff — afs-specialist-migrator · 2026-11-15T02:37:39Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-mutation-fix` / evaluation issue `martins-vds/ai-factory-eval#22` (source PR `martins-vds/ai-factory-pilot-target#394`) · **Last commit:** ca6ea678108101e0d4ef1aba363a55e41ea48d09

### Done
- Verified `.source/` is present, read-only and pinned at `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`; completed target ancestry fetch; migration validation passed (194 files, zero errors); services, runtime, RTK and `afs-run` setup probe passed.
- Started the exact profile mutation command through `afs-run`: `python .migration/harness/tools/afs-mutation --changed-since origin/main`.
- Inspected the requested base reference and changed-code scope. `origin/copilot/bk-05f-build-route-selection-itinerary-screens` is unavailable in this checkout; `origin/main...HEAD` spans 128 source-tree paths rather than only the BK-05F view.
- The mutation run remained active after about 25 minutes with four workers; it was stopped because it was processing unrelated changed-code scope. No mutation result was produced; its raw log `.migration/runs/BK-05F/20261115T021033582265Z-mutation-changed.log` is empty and is not gate evidence.
- No production or test files were changed. The previous completed run remains 0.790 (49 killed, 13 survived); all 13 diffs are in `.migration/evidence/mutants/BK-05F.md`.

### Remaining
- [ ] Restore/provide the intended target base so the profile command selects BK-05F's changed code, then rerun changed-code mutation through `afs-run`.
- [ ] Reconcile the survivors below against the fresh run; add only missing in-scope interface tests or record/simplify equivalent mutants.
- [ ] Rerun every profile gate through `afs-run`, update the return, and validate the migration state.

### Decisions made
- Did not alter the profile command or substitute `--paths`; either would not be the required profile gate.
- Classified prior survivors #1, #14, #40 and #44 as equivalent; these details are also recorded in the return file. Several other survivors appear to conflict with assertions already present in `tests/booking/interfaces/test_route_selection.py`; they are not being called equivalent or blindly duplicated until the intended base and fresh gate context are restored.

### Blockers / questions
- Provide the correct `origin/main`/ticket-base mapping for this checkout, or confirm the intended base ref. The prescribed profile command currently selects 128 paths, so completing it here would spend mutation effort outside BK-05F and exceed a reasonable session run.

### Prior 0.790 survivor diffs and classifications
The diff identifiers below refer to the exact mutation diffs in `.migration/evidence/mutants/BK-05F.md`.
- `views.py:22 #1`: `'booking.route_selection'` → `'XXbooking.route_selectionXX'` — equivalent: producer and consumer use the same domain-separation label; changing its spelling does not alter the route-selection flow.
- `views.py:22 #2`: salt → `None` — missing security-boundary test: verify a token signed without the route-selection salt is rejected.
- `views.py:29 #5`: remove route-selection `require_http_methods(['GET', 'POST'])` — test-context discrepancy: the current interface test asserts PUT returns 405, but the prior mutation report says this survived; verify with the correct base before adding a direct-view assertion.
- `views.py:34 #10`: change POST unknown-cargo 404 detail — missing interface test: POST for an unknown tracking ID and assert the 404 detail shown.
- `views.py:37 #13`: change stale-route 404 detail — missing interface test: submit a candidate that no longer satisfies the route specification and assert the user-visible 404.
- `views.py:39 #14`: `quote(..., safe="")` → `quote(..., safe="XXXX")` — equivalent: `X` is unreserved and is not percent-encoded by `quote` either way.
- `views.py:44 #16`: change route-screen no-candidate guidance — evidence discrepancy: an existing interface test asserts this exact text; confirm why the prior mutation context did not kill it.
- `views.py:48 #20`: remove itinerary `require_http_methods(['GET'])` — test-context discrepancy: the current interface test asserts POST returns 405, but the prior mutation report says this survived; verify with the correct base before adding a direct-view assertion.
- `views.py:54 #21`: change itinerary no-candidate guidance — evidence discrepancy: an existing interface test asserts this exact text; confirm why the prior mutation context did not kill it.
- `views.py:70 #27`: change GET unknown-cargo 404 detail — evidence discrepancy: the current interface test matches this exact `Http404` detail; confirm why the prior mutation context did not kill it.
- `views.py:95 #40`: missing-candidate default `''` → `'XXXX'` — equivalent: either malformed token is rejected by the same handler and produces the same 404.
- `views.py:97 #44`: change internal `BadSignature` detail — equivalent: the exception is caught and replaced by the same user-facing `Http404`.
- `views.py:100 #46`: change invalid-candidate 404 detail — missing interface assertion: assert the invalid-route detail shown for a tampered candidate, not status alone.

### Failing commands
- `rtk .migration/harness/tools/afs-run --ticket BK-05F --name mutation-changed -- python .migration/harness/tools/afs-mutation --changed-since origin/main` → interrupted before completion; no exit/result, see empty `.migration/runs/BK-05F/20261115T021033582265Z-mutation-changed.log`.

### Next step for the next session
Make the target base for this checkout resolve to the BK-05F base, rerun the exact profile mutation command, and use its fresh survivor file to resolve the outstanding test-context discrepancies before running the remaining profile gates.
