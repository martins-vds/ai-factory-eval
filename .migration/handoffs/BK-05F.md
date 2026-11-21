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

## Handoff — afs-migrator · 2026-11-21T13:24:30Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-fix-changed-code-mutation-59109fd5-857e-454b-ada8-d9e907ca20a5` / https://github.com/martins-vds/ai-factory-eval/pull/2015 · **Last commit:** `843dc53d`

### Done
- Changed-code mutation passes at 0.933 (56 killed, 4 equivalent survivors), `.migration/runs/BK-05F/20261121T131616030942Z-mutation_changed.log`; all four survivors and their diffs are in `.migration/evidence/mutants/BK-05F.md`.
- Build, idiom, behavior and CRAP profile gates pass; 469 tests pass and max CRAP is 26.0. The complete journal is `.migration/evidence/runs/BK-05F.md`.
- Added an interface test that verifies a candidate signed with the established route salt remains assignable; strengthened the no-route guidance assertions.

### Remaining
- [ ] Resolve the business-rule layer blocker without expanding BK-05F's approved file scope.
- [ ] Update the affected ledger entries and return with the use-case rules/tests once the scope is approved, then rerun migration validation.

### Decisions made
- The four mutation survivors are equivalent: #10, #13 and #44 change `Http404` messages hidden by the generic 404 response with `DEBUG=False`; #14 adds `X`, an unreserved character that `urllib.parse.quote` leaves unquoted regardless of `safe`.
- Did not change application routing code because `src/cargotracker/booking/application/routing.py` and `tests/booking/application/test_routing.py` are not in BK-05F's planned files.

### Blockers / questions
- Migration validation requires `rules` or `no_rules` for all four BK-05F capabilities, with direct use-case tests for business rules. The route-specification check is currently in the route-selection view; `CargoRouting.assign_route` accepts an itinerary without checking the current specification. Moving that rule into the application use case requires changes outside BK-05F's approved scope. The orchestrator/operator must authorize a follow-up ticket or scope change before a fresh agent edits those files.

### Failing commands
- `python .migration/harness/tools/validate.py .migration` through `afs-run` → exit 1, see `.migration/runs/BK-05F/20261121T132403492619Z-validate-rules-blocker.log:2-6`.

### Next step for the next session
Ask the orchestrator to scope a follow-up for application-layer route-specification validation and its direct use-case test; once authorized, resolve that rule, add the capability ledger rules/no-rules declarations, update the return, and validate `.migration`.
