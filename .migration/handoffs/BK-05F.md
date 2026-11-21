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

## Handoff — afs-migrator · 2026-11-21T00:08:01Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-fix-changed-code-mutation-3d762521-2422-4a76-b46d-31685371a63d` / https://github.com/martins-vds/ai-factory-eval/pull/1909 · **Last commit:** 5de91b59

### Done
- Setup passed; source SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d` matches `.migration/source.lock`.
- Added interface coverage for route-purpose signing, missing candidate rejection, and exact empty-state text. The exact guidance assertions were proven red against mutants #16 and #21 and green when restored.
- Final changed-code mutation passed: 0.891 (57 killed, 7 survived), `.migration/evidence/runs/BK-05F.md`; the current seven survivor diffs and classifications are in `.migration/returns/BK-05F.afs-migrator.yaml`.
- Profile build, behavior (470 tests), idiom, and CRAP gates passed through `afs-run`; CodeQL found 0 alerts.

### Remaining
- [ ] Resolve the business-rule layer/scope blocker below; then complete the Migrator return requirements and rerun validation.
- [ ] Rerun the full profile gates after any authorized out-of-scope change.

### Decisions made
- Missing candidate tokens are rejected explicitly before signature decoding; the response remains the same 404.
- The guidance mutants were missing exact page assertions: substring checks accepted the expected text inside the mutant’s `XX...XX` wrapper.
- The seven remaining mutants are documented as equivalent: six only change `Http404` diagnostics not rendered by the configured default `DEBUG=False` error page (the inner `BadSignature` message is wrapped), and `safe="XXXX"` produces the same quoting as `safe=""` because `X` is always unreserved.

### Blockers / questions
- The current task requires role `afs-migrator`. Its contract requires every business rule to have a direct use-case test proving refusal. `booking.routing-assign` has a current-route-specification eligibility check in `src/cargotracker/booking/interfaces/route_selection/views.py`, but `CargoRouting.assign_route` does not enforce that rule. Correcting this requires `src/cargotracker/booking/application/routing.py` and a direct test in `tests/booking/application/test_routing.py`, neither of which is in BK-05F’s permitted file list. Stop rule: do not touch these paths without the coordinator’s scope extension or human ruling.

### Failing commands
- Intentional red confirmation for guidance mutant #16: `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_explain_when_no_candidates_satisfy_the_deadline` → exit 1, `.migration/runs/BK-05F/20261120T235745504154Z-no-route-guidance-mutant-red.log`.
- Intentional red confirmation for guidance mutant #21: `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_explain_when_no_candidates_satisfy_the_deadline` → exit 1, `.migration/runs/BK-05F/20261120T235758813324Z-itinerary-guidance-mutant-red.log`.

### Next step for the next session
Ask the coordinator/operator either to extend BK-05F scope to the application routing use case and its application test, or to rule that this eligibility check is not a business rule. Then resume from this section, satisfy the applicable direct-use-case rule proof, rerun gates, and finalize the return.
