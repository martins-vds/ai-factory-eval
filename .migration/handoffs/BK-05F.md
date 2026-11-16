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

## Handoff — afs-specialist-migrator · 2026-11-16T02:03:38Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-classify-survivors-another-one` / target PR https://github.com/martins-vds/ai-factory-pilot-target/pull/394 (merged; named base branch is not present locally) · **Last commit:** c7f98b24

### Done
- Setup passed; source SHA is `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- Ran the profile mutation command first through `afs-run`: exit 0, `AFS-RESULT gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main`; log `.migration/runs/BK-05F/20261116T020054740541Z-mutation-changed.log`. The committed journal row records this result.
- Inspected the survivor diffs in `.migration/evidence/mutants/BK-05F.md` and the in-scope route-selection implementation and tests.

### Remaining
- [ ] Resume on a checkout where the BK-05F planned production code is changed relative to `origin/main`, then rerun the exact profile mutation command.
- [ ] Investigate why mutants #5, #16, #20, #21, and #27 survive despite existing tests explicitly asserting the mutated method restriction, guidance, or missing-cargo behavior.
- [ ] Consider an interface test that posts a candidate signed with the stable `booking.route_selection` salt; this should reject mutants #1 and #2.
- [ ] Re-run every profile gate, CodeQL, update the return, and validate the migration state.

### Decisions made
- No production or test files were changed: the active branch differs from `origin/main` only by migration evidence, so the profile mutation command cannot measure BK-05F code in this checkout.
- Survivor classifications from their recorded diffs:
  - #1 (`_CANDIDATE_SALT` changes to `XXbooking.route_selection`) and #2 (changes to `None`): **missing test**. An interface test should submit a candidate signed with the stable salt and assert assignment redirects to cargo details.
  - #5 (removes the GET/POST decorator): **existing-test inconsistency**. `test_route_screens_reject_unsupported_http_methods` sends PUT to this route and asserts 405; the survivor needs reproduction on the correct changed-code base, not a duplicate assertion.
  - #10 (changes the POST unknown-cargo `Http404` text) and #13 (changes the route-specification `Http404` text): **equivalent at the UI boundary**; both remain 404 responses and those diagnostic strings are not rendered by the route-selection templates.
  - #14 (changes `quote(..., safe="")` to `safe="XXXX"`): **equivalent**; alphanumeric safe characters are already unescaped by `quote`, while `/` remains encoded.
  - #16 and #21 (change the two no-route guidance strings): **existing-test inconsistency**; `test_route_screens_explain_when_no_candidates_satisfy_the_deadline` asserts both exact strings.
  - #20 (removes the itinerary GET-only decorator): **existing-test inconsistency**; `test_route_screens_reject_unsupported_http_methods` POSTs to the itinerary route and asserts 405.
  - #27 (changes the missing-cargo `Http404` text in `_selection_context`): **existing-test inconsistency**; `test_route_selection_raises_not_found_for_unknown_cargo` asserts the exact exception text.
  - #40 (changes the missing-candidate fallback from `''` to `'XXXX'`): **equivalent**; either unsigned value fails signature verification and is normalized to the same 404.
  - #44 (changes the `BadSignature` detail): **equivalent**; the exception is caught and normalized to the same `Http404`.
  - #46 (changes the invalid-candidate `Http404` detail): **equivalent at the UI boundary**; the route returns the same 404 and the diagnostic text is not rendered by the route-selection template.

### Blockers / questions
- The task names base `copilot/bk-05f-build-route-selection-itinerary-screens`, but the checked-out branch is `copilot/bk-05f-classify-survivors-another-one`; the named base ref is absent. The required changed-code command consequently reports no mutable code and cannot produce a comparable score.

### Failing commands
- None in this session. The required mutation command exited 0 with `score=n/a` (not a passing numeric mutation score).

### Next step for the next session
Restore the BK-05F planned production diff against `origin/main` on the intended base, then rerun `afs-run --ticket BK-05F --name mutation-changed -- python .migration/harness/tools/afs-mutation --changed-since origin/main`; resolve the test/report inconsistencies before claiming a mutation score.
