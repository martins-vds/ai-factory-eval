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

## Handoff — afs-migrator · 2026-11-17T21:15:00Z
**State:** blocked · **Branch / PR:** `copilot/fix-41807230-1458293352-5074cf47-3fd8-4e74-9b31-687dc0379829` / target PR #394 is already merged · **Last commit:** `61364843b1cf843321e1be015324ace5eae72423`

### Done
- Setup passed; source SHA is pinned at `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- Ran the profile mutation command first through `afs-run`. The command exited 0 but reported `score=n/a reason=no-mutable-code-changed base=origin/main`; see `.migration/evidence/runs/BK-05F.md` and `.migration/runs/BK-05F/20261117T211008307262Z-mutation-changed.log`.
- Compared the prior 13-survivor report with `tests/booking/interfaces/test_route_selection.py`; several survivors conflict with assertions already present in that file.

### Remaining
- [ ] Resume in the checkout containing BK-05F's changed code relative to the profile baseline; rerun mutation first and address the actual survivors.
- [ ] Rerun every profile gate through `afs-run`, then update this return with fresh results.

### Decisions made
- Did not edit application code or tests: `origin/main` contains no mutable BK-05F diff to score, so a no-op `n/a` is not accepted as meeting the 0.8 threshold.

### Blockers / questions
- The instructed base branch `copilot/bk-05f-build-route-selection-itinerary-screens` is not present in this repository's remote refs. The current checkout is `copilot/fix-41807230-1458293352-5074cf47-3fd8-4e74-9b31-687dc0379829`, and `git diff origin/main...HEAD` has no changed files. The exact profile command therefore cannot evaluate the intended changed code here.
- Survivor classifications from `.migration/evidence/mutants/BK-05F.md` (diff → classification):
  - #1 `_CANDIDATE_SALT = 'booking.route_selection'` → `'XXbooking.route_selectionXX'`: **missing test**; use an interface POST with a valid candidate signed independently with the expected salt, then assert the details redirect.
  - #2 `_CANDIDATE_SALT = 'booking.route_selection'` → `None`: **missing test**; the same independently signed-candidate interface assertion covers this.
  - #5 removes `@require_http_methods(['GET', 'POST'])`: **missing test in the mutation execution set**; the current interface test already asserts PUT returns 405, so this survivor conflicts with the checked-in test.
  - #10 changes the missing-cargo `Http404` detail on POST: **equivalent at the normal user interface**; the response remains 404 and the exception detail is not rendered.
  - #13 changes the route-specification `Http404` detail: **equivalent at the normal user interface**; the response remains 404 and the exception detail is not rendered.
  - #14 changes `quote(..., safe="")` to `quote(..., safe="XXXX")`: **equivalent**; `X` is always an unreserved character for `urllib.parse.quote`, so the output is unchanged.
  - #16 changes the no-route guidance on the route screen: **missing test in the mutation execution set**; the current interface test asserts the exact guidance, so this survivor conflicts with the checked-in test.
  - #20 removes `@require_http_methods(['GET'])`: **missing test in the mutation execution set**; the current interface test already asserts POST returns 405, so this survivor conflicts with the checked-in test.
  - #21 changes the no-route guidance on the itinerary screen: **missing test in the mutation execution set**; the current interface test asserts the exact guidance, so this survivor conflicts with the checked-in test.
  - #27 changes the missing-cargo `Http404` detail on GET: **missing test in the mutation execution set**; the current direct-view interface test matches this detail, so this survivor conflicts with the checked-in test.
  - #40 changes the missing-candidate default from `''` to `'XXXX'`: **equivalent**; both are invalid signing payloads and become the same 404 response.
  - #44 changes the `BadSignature` detail for a cross-cargo candidate: **equivalent**; the exception is caught and replaced by the same invalid-route 404.
  - #46 changes the invalid-route `Http404` detail: **equivalent at the normal user interface**; the response remains 404 and the exception detail is not rendered.
- The prior survivor report predates this checkout's state and cannot resolve the contradictions above without a mutation run against the intended changed-code base.

### Failing commands
- `python .migration/harness/tools/afs-mutation --changed-since origin/main` → exit 0, but result is `n/a: no mutable code changed`; see `.migration/runs/BK-05F/20261117T211008307262Z-mutation-changed.log`.

### Next step for the next session
Restore the intended BK-05F base/diff in a checkout where the profile's `origin/main` comparison includes the planned production file, then rerun the mutation gate before making any change.
