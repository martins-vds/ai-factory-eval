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

## Handoff — afs-specialist-migrator · 2026-11-16T04:21:17Z
**State:** blocked · **Branch / PR:** `copilot/fix-41807230-1458293352-ef7f62da-8bd5-4ce9-a205-e1d97ee21951` / https://github.com/martins-vds/ai-factory-eval/pull/517 · **Last commit:** 7df0d931

### Done
- Tightened the empty-route interface assertions to match the complete status paragraph and anchored the unknown-cargo error assertion; added a route-assignment interface test using a previously signed candidate token.
- Focused interface tests passed. The scoped-path mutation diagnostic passed at 0.903 (56 killed, 6 survived); this is diagnostic only and is not the profile changed-code score. See `.migration/evidence/runs/BK-05F.md` and `.migration/evidence/mutants/BK-05F.md`.
- Final profile gates via `afs-run`: compile and Django checks passed; Ruff check and format passed; behavior suite passed (469 tests); CRAP max was 26.0 against 30.
- Exact profile mutation command exited 0 but reported `AFS-RESULT gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main`.
- Migration validation passed (194 files, zero errors). CodeQL was invoked and skipped because all code changes are test-only.

### Remaining
- [ ] Run the exact changed-code mutation command on the intended BK-05F branch/base where `views.py` is changed relative to the configured base.
- [ ] If the profile gate yields a numeric result, update this return with that exact result and remove this handoff only after acceptance.

### Decisions made
- The six diagnostic survivors are equivalent at the UI boundary:
  - `views.py:34 #10`: `Http404(f'Cargo with tracking ID {tracking_id} not found.')` → `Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')`; unchanged 404 status/page, reason not rendered.
  - `views.py:37 #13`: `Http404('The selected route no longer satisfies the route specification.')` → `Http404('XXThe selected route no longer satisfies the route specification.XX')`; unchanged 404 status/page, reason not rendered.
  - `views.py:39 #14`: `quote(tracking_id, safe='')` → `quote(tracking_id, safe='XXXX')`; X is always unescaped as an unreserved character, so the redirect is identical.
  - `views.py:95 #40`: missing candidate default `''` → `'XXXX'`; both tokens fail signature verification and return the same 404.
  - `views.py:97 #44`: `BadSignature('Candidate belongs to another cargo.')` → `BadSignature('XXCandidate belongs to another cargo.XX')`; both are caught and normalized to the same 404.
  - `views.py:100 #46`: `Http404('The selected route is invalid.')` → `Http404('XXThe selected route is invalid.XX')`; unchanged 404 status/page, reason not rendered.
- Do not report the scoped-path diagnostic score as `mutation_changed`: the profile command uses `--changed-since origin/main`, and this checkout has no mutable production code in that diff.

### Blockers / questions
- The provided task says the base is `copilot/bk-05f-build-route-selection-itinerary-screens`, but this evaluation checkout is on `copilot/fix-41807230-1458293352-ef7f62da-8bd5-4ce9-a205-e1d97ee21951`; `origin/main` already contains the BK-05F implementation. A test-only change cannot make the profile command mutate `views.py`. The operator must supply the intended pre-ticket base/branch or an approved changed-code base; do not make a cosmetic production edit solely to force mutation scope.

### Failing commands
- None. The profile mutation command exited 0 with a non-applicable (`n/a`) result; the explicit-path diagnostic is not a substitute.

### Next step for the next session
Obtain the intended BK-05F branch/base, run `python .migration/harness/tools/afs-mutation --changed-since origin/main` through `afs-run`, and update the return with that profile result.
