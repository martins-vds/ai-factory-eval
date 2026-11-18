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

## Handoff — afs-migrator · 2026-11-18T03:02:41Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-fix-changed-code-mutation-e092fca1-fcaf-48cd-b718-cc7f919a7386` / target PR https://github.com/martins-vds/ai-factory-pilot-target/pull/394 (reference only) · **Last commit:** 4353d86

### Done
- Setup checks passed: source SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d` matches `.migration/source.lock`; migration validation, inputs, services and Python runtime passed.
- Ran the required mutation gate first: `afs-run --ticket BK-05F --name mutation_changed -- python .migration/harness/tools/afs-mutation --changed-since origin/main` → exit 0, `score=n/a reason=no-mutable-code-changed`, log `.migration/runs/BK-05F/20261118T025944707612Z-mutation_changed.log`; journal `.migration/evidence/runs/BK-05F.md`.
- The current checkout has no source/test diff from `origin/main` for BK-05F, and the intended target base branch `copilot/bk-05f-build-route-selection-itinerary-screens` is not present in this repository's refs. `origin` points to `martins-vds/ai-factory-eval`, while the profile target is `martins-vds/ai-factory-pilot-target`.

### Remaining
- [ ] Resume in a checkout of the intended target PR branch where BK-05F's changed production code is available relative to its target `origin/main`.
- [ ] Re-run the exact changed-code mutation gate, classify its fresh survivor diffs, and address missing interface coverage or equivalent mutants.
- [ ] Run all profile gates, update the return, and validate the migration state.

### Decisions made
- No production or test files were changed: this checkout has no mutable BK-05F code, so changing unrelated code to manufacture a mutation run would be out of scope.
- The previous survivor report `.migration/evidence/mutants/BK-05F.md` is historical (2026-11-07), not output from this session. Its classifications below are provisional until reproduced on the intended branch.
- Historical survivor classifications (diffs are recorded in `.migration/evidence/mutants/BK-05F.md`):
  - #1 (`_CANDIDATE_SALT` changed to `XXbooking.route_selectionXX`) and #2 (salt changed to `None`): **missing interface coverage** for canonical route-selection signatures; add a test that submits a canonically signed candidate and asserts the resulting details page/redirect, plus rejection of a token from another signing context. The same-request round trip does not distinguish changed signing salts.
  - #5 (remove route GET/POST decorator): **missing interface coverage** for unsupported methods; assert a PUT to the route-selection URL returns 405. The current test file appears to contain this assertion, so this conflicts with the historical survivor report.
  - #10 (prefix/suffix the missing-cargo `Http404` detail): **equivalent at the rendered interface** if both versions return the same generic 404 page; detail-level logging/error semantics must be checked on the intended branch.
  - #13 (prefix/suffix the stale-route `Http404` detail): **equivalent at the rendered interface** under the same generic-404 condition; detail-level logging/error semantics must be checked on the intended branch.
  - #14 (`quote(..., safe="")` changed to `safe="XXXX"`): **equivalent** for this diff because `X` is unreserved and already left unescaped by `quote`.
  - #16 (prefix/suffix the empty-route guidance): **missing interface coverage** for exact visible guidance; the current test file appears to assert the unmutated text, conflicting with the historical survivor report.
  - #20 (remove itinerary GET-only decorator): **missing interface coverage** for POST returning 405; the current test file appears to assert this, conflicting with the historical survivor report.
  - #21 (prefix/suffix the itinerary empty-route guidance): **missing interface coverage** for exact visible guidance; the current test file appears to assert the unmutated text, conflicting with the historical survivor report.
  - #27 (prefix/suffix missing-cargo detail in the selection context): **missing interface coverage** for the unknown-cargo response; the current test directly asserts the `Http404` message, conflicting with the historical survivor report.
  - #40 (missing candidate default changed from `''` to `'XXXX'`): **equivalent at the rendered interface** if either invalid token leads to the same generic 404 page.
  - #44 (change the caught `BadSignature` detail): **equivalent** because the detail is caught and converted to the same generic `Http404` response.
  - #46 (prefix/suffix the invalid-selection `Http404` detail): **equivalent at the rendered interface** under the generic-404 behavior; detail-level logging/error semantics must be checked on the intended branch.

### Blockers / questions
- This eval checkout is not the target PR checkout. The profile's target repository and requested PR base branch do not match the configured `origin`; no mutation score can be obtained from the exact profile command here. The intended target checkout must be supplied before code changes or full gates can be completed.

### Failing commands
- None. The mutation command exited 0 but reported no mutable code; it is not a passing numeric mutation score.

### Next step for the next session
Re-run setup in the target checkout for `martins-vds/ai-factory-pilot-target` on `copilot/bk-05f-build-route-selection-itinerary-screens`, then run its profile mutation command before editing anything.
