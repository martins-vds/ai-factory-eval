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

## Handoff — afs-specialist-migrator · 2026-11-15T20:16:23Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-fix-changed-code-mutation-again` / https://github.com/martins-vds/ai-factory-pilot-target/pull/394 · **Last commit:** 659cf82

### Done
- AFS setup passed: source SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d` matches `.migration/source.lock`; target history is complete; services and Python 3.13.18 are healthy.
- Ran the exact profile mutation command first via `afs-run`: `python .migration/harness/tools/afs-mutation --changed-since origin/main`. It returned `score=n/a reason=no-mutable-code-changed` because this checkout has no mutable code delta against `origin/main`; see `.migration/runs/BK-05F/20261115T201226689039Z-mutation-changed-initial.log`.
- The current interface suite passed: 7 tests; see `.migration/runs/BK-05F/20261115T201456077966Z-route-selection-tests-current.log`.
- The target graph check still reports no matching booking route endpoints (`.migration/graphs/target/full/graph-check.md:21-25`), while the planned files and route handlers are present. The code and focused tests are clear for this task; no graph files were changed.

### Survivor classification
The saved `.migration/evidence/mutants/BK-05F.md` is from the prior 0.790 run. The current profile command could not reproduce any mutants, so these are classifications from the recorded diffs and current tests, not a fresh mutation result.

| Mutant | Recorded diff | Classification |
|---|---|---|
| #1 | `_CANDIDATE_SALT`: `'booking.route_selection'` → `'XXbooking.route_selectionXX'` | Missing interface assertion if the route-signing namespace is a stable contract: submit a candidate signed with the approved salt and assert the resulting details redirect. The current same-build round trip does not distinguish a changed salt. |
| #2 | `_CANDIDATE_SALT`: `'booking.route_selection'` → `None` | Same missing fixed-namespace assertion as #1; no production change made while the changed-code gate is inactive. |
| #5 | Remove `@require_http_methods(['GET', 'POST'])` from route selection | Already covered by `test_route_screens_reject_unsupported_http_methods`, which asserts PUT returns 405. The saved survivor conflicts with the current interface test and needs a fresh run against a mutable-code baseline. |
| #10 | Change POST-path missing-cargo `Http404` text | The GET-path unknown-cargo test checks the same message, but POST-after-cargo-removal is not exercised. Only the diagnostic text changes; add a race/404 assertion only if this text is part of the rendered interface contract. |
| #13 | Change stale route-specification `Http404` text | No UI state/redirect changes; the only difference is 404 diagnostic text. Treat as equivalent at the production interface boundary unless the project requires that diagnostic to be displayed. |
| #14 | `quote(tracking_id, safe="")` → `safe="XXXX"` | Equivalent: `X` is always unreserved and remains unescaped by `urllib.parse.quote`, so this does not change the path segment. |
| #16 | Change route-screen no-candidate guidance | Already covered by `test_route_screens_explain_when_no_candidates_satisfy_the_deadline`, which asserts the exact route-screen guidance. Saved result conflicts with the current test. |
| #20 | Remove `@require_http_methods(['GET'])` from itinerary selection | Already covered by the same method test, which asserts itinerary POST returns 405. Saved result conflicts with the current test. |
| #21 | Change itinerary-screen no-candidate guidance | Already covered by `test_route_screens_explain_when_no_candidates_satisfy_the_deadline`, which asserts the exact itinerary guidance. Saved result conflicts with the current test. |
| #27 | Change GET-path missing-cargo `Http404` text | Already covered by `test_route_selection_raises_not_found_for_unknown_cargo`, which matches the exception text. Saved result conflicts with the current test. |
| #40 | Change missing `candidate` default from `''` to `'XXXX'` | Equivalent at the interface boundary: both values fail signature validation and are normalized to the same 404. |
| #44 | Change caught `BadSignature` text | Equivalent: the exception is caught and normalized to the same 404; its internal message is not rendered. |
| #46 | Change invalid-candidate `Http404` text | Equivalent at the production interface boundary: the response remains the same 404; only its diagnostic reason changes. |

### Remaining
- [ ] Restore a checkout/base where the profile's `--changed-since origin/main` includes BK-05F mutable code, or have the operator clarify the intended mutation baseline.
- [ ] Rerun changed-code mutation. If the threshold is still missed, address only verified live survivors and rerun all profile gates through `afs-run`.
- [ ] Rerun CodeQL after any code change; validate and update the return file.

### Decisions made
- No production code was changed just to manufacture a mutation delta. The approved profile command currently selects no mutable code, and the persisted mutant report contradicts several passing interface assertions.

### Blockers / questions
- The current checkout does not expose BK-05F as mutable code to the required profile mutation gate. A score or gate pass cannot be claimed from this session.
- Confirm whether the route-signing salt and 404 diagnostic text are intended stable UI/security contracts before adding implementation-coupled assertions.

### Failing commands
- `python .migration/harness/tools/afs-mutation --changed-since origin/main` → exit 0, `score=n/a reason=no-mutable-code-changed`; see `.migration/runs/BK-05F/20261115T201226689039Z-mutation-changed-initial.log`.

### Next step for the next session
Resume from this section, first establish the intended changed-code base for BK-05F, then rerun the exact profile mutation command before editing code.
