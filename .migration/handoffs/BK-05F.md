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

## Handoff — afs-specialist-migrator · 2026-11-15T17:48:29Z
**State:** blocked · **Branch / PR:** `copilot/fix-41807230-1458293352-75f360eb-e54a-4071-98f5-9d0b87086bc4` / eval task for `martins-vds/ai-factory-pilot-target#394` · **Last commit:** d698b06c

### Done
- Setup passed: source SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d` matched, target history was complete, migration validation had zero errors, services were healthy, and Python 3.13.18 matched the profile.
- Ran the profile mutation command first via `afs-run`: `python .migration/harness/tools/afs-mutation --changed-since origin/main` → exit 0, `AFS-RESULT gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main`; see `.migration/runs/BK-05F/20261115T174829693364Z-mutation-changed-initial.log`.
- The eval checkout's `origin/main` is commit `3340e60a1416477a02dd9f9c4937c5fdd67b96b8` (parent `4ce1c99ca2c5947a41266953cb0e3a305703dc8d`) and already contains the route-selection implementation and tests. The only task-branch diff is evidence journaling; no BK-05F production change is eligible for changed-code mutation here.
- Classified every survivor in the checked-in `.migration/evidence/mutants/BK-05F.md` against the current tree:

| Mutant | Diff | Classification |
|---|---|---|
| #1 | `_CANDIDATE_SALT`: `'booking.route_selection'` → `'XXbooking.route_selectionXX'` | Missing interface assertion: submit a candidate signed with the specified route-selection salt and assert assignment redirects to cargo details. |
| #2 | `_CANDIDATE_SALT`: `'booking.route_selection'` → `None` | Missing interface assertion: same fixed-salt submission should reject a missing/other salt and accept the specified salt; this also distinguishes #1. |
| #5 | Remove route-selection `@require_http_methods(['GET', 'POST'])` | Covered in current tree: `test_route_screens_reject_unsupported_http_methods` asserts PUT returns 405. The stored survivor report is stale relative to current tests. |
| #10 | Wrap the POST missing-cargo `Http404` message in `XX` | Missing interface assertion: the missing-cargo POST response should show the expected not-found message. |
| #13 | Wrap the route-specification `Http404` message in `XX` | Missing interface assertion: a now-invalid candidate response should show the expected route-specification error. |
| #14 | `quote(tracking_id, safe="")` → `quote(tracking_id, safe="XXXX")` | Equivalent: `X` is always unreserved by `urllib.parse.quote`, so adding it to `safe` cannot change encoding. |
| #16 | Wrap route-page no-route guidance in `XX` | Covered in current tree: `test_route_screens_explain_when_no_candidates_satisfy_the_deadline` asserts the exact route-page guidance. Stored survivor report is stale. |
| #20 | Remove itinerary-page `@require_http_methods(['GET'])` | Covered in current tree: `test_route_screens_reject_unsupported_http_methods` asserts POST returns 405. Stored survivor report is stale. |
| #21 | Wrap itinerary-page no-route guidance in `XX` | Covered in current tree: `test_route_screens_explain_when_no_candidates_satisfy_the_deadline` asserts the exact itinerary-page guidance. Stored survivor report is stale. |
| #27 | Wrap the GET missing-cargo `Http404` message in `XX` | Covered in current tree: `test_route_selection_raises_not_found_for_unknown_cargo` matches the exact message. Stored survivor report is stale. |
| #40 | Missing POST `candidate` default: `''` → `'XXXX'` | Equivalent: either value is an invalid signed candidate and follows the same invalid-route response. |
| #44 | Change the internal `BadSignature` cause message | Equivalent at the UI boundary: the caught cause is replaced by the same outer `Http404`; the internal cause text is not rendered. |
| #46 | Wrap the invalid-candidate `Http404` message in `XX` | Missing interface assertion: the invalid-candidate response should show the specified invalid-route message. |

- Current target graph evidence is stale too: `.migration/graphs/target/full/graph-check.md` names target commit `017d30113cf160f9973da8196612a0cef07701eb` and reports the BK-05F route endpoints as not built, while the current code contains them.

### Remaining
- [ ] Restore an execution checkout/ref where the profile's `origin/main` is the actual target-repository baseline for PR #394, so the route-selection production changes are included in `--changed-since origin/main`.
- [ ] Regenerate mutation evidence against that exact code/test tree; reconcile the stale survivors above with the fresh diffs.
- [ ] Add only the interface tests still needed, rerun mutation and every profile gate through `afs-run`, and update the return file.

### Decisions made
- No application or test files were changed: the current base cannot produce the requested changed-code score, and the checked-in mutant list conflicts with several current assertions.

### Blockers / questions
- The eval clone's `origin` points to `martins-vds/ai-factory-eval`, not `martins-vds/ai-factory-pilot-target`; its `origin/main` already contains BK-05F, so the specified profile mutation command has no mutable code to inspect. The original task's 0.790 score and survivor file cannot be verified against this checkout. A correct target-repository base/ref is needed before proceeding.

### Failing commands
- `python .migration/harness/tools/afs-mutation --changed-since origin/main` → exit 0 with `score=n/a reason=no-mutable-code-changed`, see `.migration/runs/BK-05F/20261115T174829693364Z-mutation-changed-initial.log`.

### Next step for the next session
Run setup in the correct target-repository PR #394 checkout, then run its profile mutation command and classify the freshly generated survivor diffs before making any code or test change.
