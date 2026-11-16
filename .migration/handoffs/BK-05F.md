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

## Handoff — afs-specialist-migrator · 2026-11-16T00:02:00Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-fix-changed-code-mutation-another-one` / https://github.com/martins-vds/ai-factory-eval/pull/430 · **Last commit:** `48b36703`
### Done
- Inlined the candidate signing salt to remove equivalent shared-constant mutants; `candidate-assignment-after-salt-inline` passed.
- Strengthened empty-state interface assertions to match the complete displayed guidance. The test failed on the `XX…XX` mutant and passed after the original text was restored (`no-route-guidance-exact-assertion-red` and `no-route-guidance-exact-assertion-green`).
- Changed-code mutation passed at 0.887 (55 killed, 7 survived): `.migration/runs/BK-05F/20261115T235549111468Z-mutation-changed-exact-guidance.log`; fresh survivor diffs are in `.migration/evidence/mutants/BK-05F.md`.
- Build compile, Django check and Ruff check passed in this session.
### Remaining
- [ ] Resolve the repository-wide `ruff format --check` failure only after an operator approves scope for `tests/conftest.py`, or provides the intended pinned formatter behavior.
- [ ] Run the full behavior and CRAP gates through `afs-run`, then update this return with final gate results.
### Decisions made
- The seven remaining mutant diffs are equivalent at the UI boundary: #8, #11, #25 and #46 alter Http404 exception text hidden by the generic 404 page; #12 adds `X` to `quote`'s safe set, but X is always unescaped; #39 changes the invalid-token fallback, with either value producing the same caught invalid-signature 404; #44 changes a BadSignature message immediately replaced by the same generic 404.
### Blockers / questions
- The required whole-repository formatter gate flags `/home/runner/work/ai-factory-eval/ai-factory-eval/tests/conftest.py:6`, which is not in BK-05F's planned file list. The ticket requires stopping and handing off rather than touching an unplanned file.
### Failing commands
- `ruff format --check` → exit 1, see `.migration/runs/BK-05F/20261116T000153620213Z-idiom-ruff-format-final.log:1-9`.
### Next step for the next session
Ask the operator to authorize the out-of-scope `tests/conftest.py` formatting change or confirm an environment-specific resolution; then rerun the full profile gates and finalize the return.
