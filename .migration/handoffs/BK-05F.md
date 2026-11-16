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

## Handoff — afs-migrator · 2026-11-16T20:37:30Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-classify-survivors-yet-again` / https://github.com/martins-vds/ai-factory-pilot-target/pull/394 · **Last commit:** a936629f

### Done
- Setup passed; source SHA is `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- Ran the required profile mutation command first via `afs-run`; command exited 0 but reported `score=n/a reason=no-mutable-code-changed base=origin/main`. Journal: `.migration/evidence/runs/BK-05F.md`; raw log: `.migration/runs/BK-05F/20261116T203635119787Z-mutation-changed.log`.
- Confirmed the checkout is not the stated base branch (`copilot/bk-05f-build-route-selection-itinerary-screens`). `git diff origin/main...HEAD` has no files, so the BK-05F implementation and tests are already in the mutation baseline and this session cannot reproduce the historical 0.790 run.
- Classified every survivor listed in `.migration/evidence/mutants/BK-05F.md` (diffs remain in that file):
  - Mutants #1 and #2 (candidate signing salt changed): equivalent within the rendered-and-submitted candidate flow; signing and verification use the same salt.
  - Mutants #5 and #20 (HTTP-method decorators removed): non-equivalent; unsupported methods can render a page instead of returning 405. Existing interface test `test_route_screens_reject_unsupported_http_methods` asserts PUT/POST return 405, so the old survivor result conflicts with the checked-in test and needs reproduction on the specified base.
  - Mutants #10, #13, #27, #44, and #46 (Http404 message text changed): equivalent at the UI boundary; the 404 response is unchanged and the exception detail is not rendered.
  - Mutant #14 (`quote(..., safe="")` changed to `safe="XXXX"`): equivalent; `X` is unreserved and is not percent-encoded by `quote` regardless of `safe`.
  - Mutants #16 and #21 (empty-route guidance changed): non-equivalent visible copy. Existing interface test `test_route_screens_explain_when_no_candidates_satisfy_the_deadline` asserts both messages, so the historical survivors conflict with the checked-in assertions and need reproduction on the specified base.
  - Mutant #40 (missing-token default changed from empty string to `XXXX`): equivalent; either value fails signature validation and produces the same 404.

### Remaining
- [ ] Resume on the specified PR base (or provide that branch's files/history in this checkout) and rerun the exact profile mutation command.
- [ ] Reproduce the four non-equivalent HTTP-method and visible-guidance mutants despite existing assertions; add an interface test only if reproduction shows a missing assertion.
- [ ] Run all profile gates through `afs-run`, update the return and validate migration outputs.

### Decisions made
- No application or test files were changed: the required mutation gate had no changed production code to analyze in this checkout, and changing code without the specified base would not establish the reported shortfall.

### Blockers / questions
- The specified base branch is unavailable in this repository checkout; current branch and baseline do not contain a mutable BK-05F code diff. The migration contract stop rule for a real setup/context limit applies.
- The stored survivor report and existing interface assertions disagree for mutants #5, #20, #16, and #21; the correct base is needed to reproduce before changing tests.
- The task requests role `afs-migrator` and return `.migration/returns/BK-05F.afs-migrator.yaml`, but the approved plan assigns BK-05F to `afs-specialist-migrator`. `validate.py` rejects a second role's return for the same ticket. The plan is out of this ticket's file scope, so a valid role return needs a coordinator decision.
- `afs-finish-check` likewise expects this session to update `.migration/returns/BK-05F.afs-specialist-migrator.yaml`; doing so would attribute this `afs-migrator` session to another role. A coordinator must resolve the role/return attribution.

### Failing commands
- `.migration/harness/tools/afs-finish-check` → exit 1: it requires updating the specialist-migrator return; see the role conflict above.
- Mutation command exited 0 with `n/a`, not a passing numeric mutation score; see `.migration/runs/BK-05F/20261116T203635119787Z-mutation-changed.log`.

### Next step for the next session
Ask the coordinator to reconcile BK-05F's role in the approved plan with this continuation's requested `afs-migrator` role, then resume on `copilot/bk-05f-build-route-selection-itinerary-screens` (or obtain its exact diff) and rerun mutation triage.
