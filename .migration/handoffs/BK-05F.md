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

## Handoff — afs-specialist-migrator · 2026-11-16T05:58:01Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-run-changed-code-mutation-again` / current evaluation task `martins-vds/ai-factory-eval#554` · **Last commit:** 6d040efa

### Done
- Setup passed: source SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d` matches `.migration/source.lock`, source is read-only/ignored, target ancestry is complete, migration validation and input checks pass, services/runtime are healthy.
- Ran the profile's changed-code mutation command first through `afs-run`: exit 0, `AFS-RESULT gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main`; see `.migration/evidence/runs/BK-05F.md` and `.migration/runs/BK-05F/20261116T055549648350Z-mutation-changed.log`.
- Confirmed `src/cargotracker/booking/interfaces/route_selection/views.py` and its planned interface test are identical to `origin/main`; this checkout has no BK-05F production diff. The required base branch `copilot/bk-05f-build-route-selection-itinerary-screens` is not present in this checkout.
- Classified every survivor in `.migration/evidence/mutants/BK-05F.md`:
  - #1 and #2 (`_CANDIDATE_SALT` changed to a different string or `None`): **missing test** — POST a candidate signed with the stable `booking.route_selection` salt to verify compatibility at the interface.
  - #5 (remove route-selection GET/POST decorator): **not equivalent; runner discrepancy** — the existing interface test already asserts PUT returns 405, so this mutant should be killed; investigate mutation test selection before adding a duplicate assertion.
  - #10 (change unknown-cargo POST 404 message): **missing test** — POST for unknown cargo and assert the 404 message.
  - #13 (change route-specification rejection message): **missing test** — POST a validly signed but specification-incompatible itinerary and assert the 404 message.
  - #14 (`quote(..., safe="")` to `safe="XXXX"`): **equivalent** — `X` is an RFC-unreserved character and is always left unescaped by `urllib.parse.quote`.
  - #16 and #21 (change no-route guidance): **not equivalent; runner discrepancy** — the existing empty-candidates interface test asserts each exact guidance string; investigate why those assertions did not kill these mutants.
  - #20 (remove itinerary GET-only decorator): **not equivalent; runner discrepancy** — the existing interface test already asserts POST returns 405; investigate mutation test selection before adding a duplicate assertion.
  - #27 (change unknown-cargo GET 404 message): **not equivalent; runner discrepancy** — the existing direct-view test matches the exact message; investigate mutation test selection or artifact freshness.
  - #40 (change missing candidate default from empty string to `"XXXX"`): **missing test** — POST without a candidate and assert the invalid-selection 404.
  - #44 (change the internal `BadSignature` message): **equivalent at the UI boundary** — the caught exception is mapped to the same generic invalid-selection 404.
  - #46 (change generic invalid-selection 404 message): **missing test** — submit a modified candidate and assert the invalid-selection message, not only the status.

### Remaining
- [ ] Resume from the correct BK-05F base with the target production change present relative to `origin/main`; do not manufacture a production diff to make this checkout's mutation gate run.
- [ ] Re-run changed-code mutation and investigate the existing-test survivors (#5, #16, #20, #21, #27); add only the genuinely missing interface assertions, then rerun the profile gates.
- [ ] Update the return with the measured mutation score, validate migration outputs, and run CodeQL after any code changes.

### Decisions made
- No application or test changes were made: this branch's mutation command has no mutable code to evaluate, and adding tests alone cannot establish the requested changed-code score.

### Blockers / questions
- This evaluation checkout is `copilot/bk-05f-run-changed-code-mutation-again`, not the task's expected `copilot/bk-05f-build-route-selection-itinerary-screens`; the exact target branch is unavailable locally, while the BK-05F implementation and tests are already on `origin/main`. The required gate therefore cannot reproduce the reported `0.790` here.

### Failing commands
- None in this session. The required mutation command exited 0 but returned `score=n/a` because no mutable code changed.

### Next step for the next session
Resume on the BK-05F worktree where the route-selection implementation is changed relative to its `origin/main`, verify that the changed-code command selects that file, then address the classified survivors and capture a numeric mutation result.
