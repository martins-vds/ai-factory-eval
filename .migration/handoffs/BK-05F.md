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

## Handoff — afs-migrator · 2026-11-20T00:46:01Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-continue-changed-code-mutation-another-one` / https://github.com/martins-vds/ai-factory-pilot-target/pull/394 (read-only reference) · **Last commit:** 0559238c

### Done
- Setup checks passed; pinned source SHA is `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- Read live issue #293, titled “BK-05F · Build route selection and itinerary screens”; it is closed by merged PR #394. No live tracker resources were changed.
- Ran the exact profile mutation command with the checkout's default `AFS_BASE=943aa43950ea415c5924f8356f9d8bb6f2fc2e84`: exit 0, but it reported `n/a: no mutable code changed` (`.migration/runs/BK-05F/20261120T003514932751Z-mutation-changed.log`). This eval base already contains the implementation.
- Tried the same command with `AFS_BASE=origin/copilot/bk-05f-build-route-selection-itinerary-screens`. That historical ref includes many unrelated changes in this eval checkout, so mutation selected unrelated `src/` files. Stopped the run before any repository edits; its log is empty and it produced no score.
- No production or test files were changed. The only fresh evidence committed so far is the setup and no-mutable-code journal rows.

### Remaining
- [ ] Restore or identify a base ref that contains all unrelated migrated work but excludes only BK-05F's implementation; rerun the exact profile mutation command against it.
- [ ] Re-evaluate the survivor classifications below with that valid run; add focused interface tests only for genuine behavior gaps, then rerun the mutation gate and every profile gate through `afs-run`.
- [ ] Update this return with fresh gate results and validate all migration outputs.

### Decisions made
- Stopped rather than mutate or score unrelated source files. The current eval `AFS_BASE` is too new to find BK-05F code changes; the named historical PR base is too old and broad for this checkout.

### Blockers / questions
- Operator must provide/restore the correct ticket-scoped base for mutation. The issue's original historical base is available, but this eval checkout contains later work not present on it; using that ref violates BK-05F's scope.
- The prior `.migration/evidence/mutants/BK-05F.md` lists these 13 survivors and their diffs. The classifications are provisional because that report predates this checkout's current eval base:
  - `views.py:22`, `'booking.route_selection'` → `'XXbooking.route_selectionXX'`: missing interface test for accepting a valid token signed with the stable salt, including a form token retained across deployment.
  - `views.py:22`, `'booking.route_selection'` → `None`: same missing interface test; a previously rendered valid candidate must remain acceptable.
  - `views.py:29`, remove `@require_http_methods(['GET', 'POST'])`: missing-test classification for the 405 response. The existing unsupported-method test appears to assert this already, so investigate why the old mutation run did not kill it before adding duplicate coverage.
  - `views.py:34`, wrap unknown-cargo 404 text in `XX`: equivalent at the production page boundary; the 404 status is unchanged and the exception detail is diagnostic.
  - `views.py:37`, wrap stale-route 404 text in `XX`: equivalent at the production page boundary; the same 404 response is returned.
  - `views.py:39`, change `quote(..., safe="")` to `safe="XXXX"`: equivalent; `X` is unreserved and remains unescaped either way.
  - `views.py:44`, wrap route-page no-route guidance in `XX`: missing-test classification because rendered guidance is user-visible. Existing no-candidate test asserts the exact text, so verify mutation test selection/cache on a valid run.
  - `views.py:48`, remove `@require_http_methods(['GET'])`: missing-test classification for the 405 response. The existing unsupported-method test appears to cover it; investigate the mutation-run discrepancy before duplicating it.
  - `views.py:54`, wrap itinerary-page no-route guidance in `XX`: missing-test classification because rendered guidance is user-visible. Existing no-candidate test asserts the exact text; verify mutation test selection/cache.
  - `views.py:70`, wrap unknown-cargo 404 text in `XX`: equivalent at the production page boundary; the exception detail is diagnostic and the 404 status is unchanged.
  - `views.py:95`, change missing-candidate default `''` to `'XXXX'`: equivalent; both values fail signature validation and produce 404.
  - `views.py:97`, change the `BadSignature` reason to `XXCandidate belongs to another cargo.XX`: equivalent; the reason is caught and replaced by the same 404 response.
  - `views.py:100`, wrap invalid-route 404 text in `XX`: equivalent at the production page boundary; the same 404 response is returned.

### Failing commands
- `AFS_BASE=origin/copilot/bk-05f-build-route-selection-itinerary-screens .migration/harness/tools/afs-run --ticket BK-05F --name mutation-changed-intended-base -- python .migration/harness/tools/afs-mutation` → interrupted before completion because it selected unrelated changed source files; empty raw log `.migration/runs/BK-05F/20261120T003616874912Z-mutation-changed-intended-base.log`.

### Next step for the next session
Resolve the eval-base mismatch by identifying a base containing the current eval tree before BK-05F's changes, then rerun changed-code mutation and every profile gate; do not score against the broad historical branch.
