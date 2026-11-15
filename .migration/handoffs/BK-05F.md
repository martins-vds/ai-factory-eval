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

## Handoff — afs-specialist-migrator · 2026-11-15T15:45:54Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-classify-survivors` / https://github.com/martins-vds/ai-factory-pilot-target/pull/394 · **Last commit:** 79f545c
### Done
- Setup passed; pinned source SHA is `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- Read the ticket, approved BK-05F files and previous handoff. The previous completed changed-code run reported 0.790 (49 killed, 13 survived); its full diffs are in `.migration/evidence/mutants/BK-05F.md` and the run result is in `.migration/evidence/runs/BK-05F.md`.
- Started the exact profile command through `afs-run`: `python .migration/harness/tools/afs-mutation --changed-since origin/main`. In this evaluation checkout, `origin/main` is `e1ea28f26a46c18c92c94fcb78e1af3bc60e673b`; the diff to HEAD is 803 files, including 128 Python files under `src` (4,537 lines). This does not match the live BK-05F run's one changed production file. After 41 minutes it was still mutating unrelated `cargo/domain/cargo.py`; the run was stopped without an `AFS-RESULT`, and no successful gate row was recorded. The empty partial log is `.migration/runs/BK-05F/20261115T150311801964Z-mutation-changed.log`.
### Remaining
- [ ] Make the actual BK-05F base available to this checkout (or resume in the correct target-repository branch) so the profile command measures the planned BK-05F changes rather than 128 unrelated Python files.
- [ ] Re-run changed-code mutation first, inspect the fresh diffs, and finish classifying them. The prior 13 are provisionally classified below; revalidate the apparent conflicts against the fresh run.
- [ ] Add/strengthen the public-interface test for default-salt candidate tokens if mutant #2 remains; resolve the method-restriction and guidance-text survivors if they remain after the base is corrected.
- [ ] Run every profile gate through `afs-run`, update the return, and validate `.migration`.
### Decisions made
- Existing mutant #1 (salt `'booking.route_selection'` → `'XXbooking.route_selectionXX'`) is provisionally equivalent at the UI boundary: the same view signs and validates its candidate token, and no cross-deployment token compatibility requirement is recorded.
- Existing mutants #10 and #27 (404 detail text changes), #13 (stale-route 404 detail), #44 and #46 (invalid-candidate error text) are provisionally equivalent for the normal user-facing 404 page; the detail is not rendered when debug mode is off. Mutant #40 (`''` → `'XXXX'` for the submitted token default) is equivalent because either value is rejected as an invalid signature.
- Existing mutant #14 (`quote(..., safe="")` → `quote(..., safe="XXXX")`) is equivalent because `X` is unreserved and remains unescaped by `urllib.parse.quote`.
- Existing mutant #2 (salt → `None`) is non-equivalent: it removes the route-specific signing namespace. A focused POST test can submit a candidate signed with Django's default signer and assert the request remains 404 and the cargo details page remains unrouted.
- Existing mutants #5 and #20 (removing the route and itinerary HTTP-method decorators) are non-equivalent: unsupported methods must remain 405. The current interface test already asserts these cases, so the survivor conflicts with the expected test behavior and must be investigated on a correctly based run.
- Existing mutants #16 and #21 (changing route/itinerary no-candidate guidance) are non-equivalent because the rendered page text changes. The current empty-state interface test already asserts both literal messages, so these survivors also need fresh-run investigation rather than being silently accepted.
### Blockers / questions
- This clone's `origin/main` is the eval repository baseline, not the live ticket base `copilot/bk-05f-build-route-selection-itinerary-screens` (that branch is not available here). The exact profile mutation gate therefore expands far beyond BK-05F and did not finish in a reasonable session window. A human must provide the correct base ref or dispatch this ticket in the live target-repository checkout.
### Failing commands
- `.migration/harness/tools/afs-run --ticket BK-05F --name mutation-changed -- python .migration/harness/tools/afs-mutation --changed-since origin/main` → interrupted after 41 minutes; no exit/result, see `.migration/runs/BK-05F/20261115T150311801964Z-mutation-changed.log`.
### Next step for the next session
Re-run setup in a checkout where `origin/main` is the BK-05F ticket base, then rerun the exact profile mutation command before editing; compare its fresh survivor diffs with the classifications above and proceed only within BK-05F's planned files.
