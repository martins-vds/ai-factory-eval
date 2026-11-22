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

## Handoff — afs-migrator · 2026-11-22T17:45:03Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-changed-code-mutation-fix-again` / requested live base `copilot/bk-05f-build-route-selection-itinerary-screens` (PR #394) · **Last commit:** 8dbb2c0

### Done
- Setup checks passed: source SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d` matches the pin, is read-only and ignored; services and runtimes are healthy.
- Ran the profile's exact changed-code command through `afs-run`: exit 0, but `AFS-RESULT gate=mutation score=n/a reason=no-mutable-code-changed base=1fd8c48200934554a753ec1a33c9eb0119052bfc`; log `.migration/runs/BK-05F/20261122T174126394369Z-mutation-changed.log`.
- The specified starting commit was `4ce1c99ca2c5`; this checkout started at `c3678996d577a1659d665aac20896219648657a4` on a different branch. The BK-05F source, templates and tests have no diff from the mutation base. No live target branch was fetched, checked out or merged.
- Classified the recorded survivors from their diffs, but the classifications cannot be verified against a mutation run on the requested base:
  - #1 equivalent for this screen's self-issued token flow: dump and load use the same salt, with no rendered change.
  - #2 missing security-interface test: POST an otherwise valid default-signed (unsalted) candidate and assert the user receives 404 and the cargo remains unrouted; salt=None would accept it.
  - #5 missing/observable method guard: removing the decorator changes PUT from 405 to a rendered route page. The current test already asserts 405, so this conflicts with the survivor report.
  - #10 equivalent at the UI boundary: changing the unknown-cargo 404 reason does not change the 404 response.
  - #13 equivalent at the UI boundary: changing the stale-route 404 reason does not change the 404 response.
  - #14 equivalent: adding `X` to quote's safe set has no effect because `X` is unreserved already.
  - #16 missing/observable guidance assertion: the changed text is rendered when there are no routes. The current empty-state test already asserts it, so this conflicts with the survivor report.
  - #20 missing/observable method guard: removing the GET-only decorator changes POST from 405 to a rendered page. The current unsupported-method test already asserts 405, so this conflicts with the survivor report.
  - #21 missing/observable itinerary guidance assertion: the changed text is rendered. The current empty-state test already asserts it, so this conflicts with the survivor report.
  - #27 equivalent at the UI boundary: the changed unknown-cargo 404 reason is not shown in the 404 page; the current direct-view test also asserts the original reason, so this conflicts with the survivor report.
  - #40 equivalent: both the empty string and `XXXX` are invalid signatures and lead to the same 404.
  - #44 equivalent: the changed BadSignature detail is caught and mapped to the same 404.
  - #46 equivalent at the UI boundary: changing the invalid-route 404 reason does not change the response.

### Remaining
- [ ] Resume on the requested BK-05F base commit and rerun the profile mutation command so its changed-code selection and survivor report are authoritative.
- [ ] Reconcile the reported survivors with the existing method/guidance/unknown-cargo assertions; add only genuinely missing interface coverage, then rerun mutation and every profile gate.
- [ ] Update the ticket return with verified gate results and run migration validation.

### Decisions made
- No application or test changes were made: this checkout has no mutable BK-05F code diff, and adding tests here cannot produce the requested changed-code score.

### Blockers / questions
- The checkout branch and starting commit do not match the issue's specified base. The profile mutation gate therefore reports no mutable code changed instead of reproducing the stated 0.790 score. Do not manufacture a baseline or use `--paths`/`--all`; restore the requested ticket checkout before continuing.

### Failing commands
- None. The profile mutation command exited 0 but returned `score=n/a`; see `.migration/runs/BK-05F/20261122T174126394369Z-mutation-changed.log`.

### Next step for the next session
Restore the checkout to the requested BK-05F base at `4ce1c99ca2c5` without fetching or merging the live target branch, rerun setup and the exact profile mutation gate, and resolve the authoritative survivor list before editing.
