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

## Handoff — afs-specialist-migrator · 2026-11-16T15:33:34Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-fix-changed-code-mutation-one-more-time` / https://github.com/martins-vds/ai-factory-pilot-target/pull/394 · **Last commit:** 2f7f0886

### Done
- Setup passed; source SHA is `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- The profile's changed-code mutation command ran first: exit 0, but `AFS-RESULT gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main` (`.migration/runs/BK-05F/20261116T152853398139Z-mutation-changed.log`). The current diff against `origin/main` contains only evidence; no mutable source code differs, so this does not verify the required 0.8 score.
- Build passed (`build-compile`, `build-django-check`); idiom passed (`idiom-ruff-check`, `idiom-ruff-format`); behavior passed with 468 tests; CRAP passed at 26.0. All runs are in `.migration/evidence/runs/BK-05F.md`.
- Classified all 13 entries in the prior `.migration/evidence/mutants/BK-05F.md` report against current source and tests:
  - **Equivalent:** #1 and #2 change the shared candidate-signing salt, so candidates are still signed and checked with the same opaque salt; #10 and #13 change only `Http404` details, not the 404 page; #14 adds `X` to URL quoting's safe characters, but `X` is unreserved and remains unescaped either way; #40 changes one invalid/missing-token value to another and both produce the same invalid-candidate 404; #44 changes an internal `BadSignature` detail that is replaced by the same 404; #46 changes the internal 404 detail, not the page.
  - **Already covered; prior survivor report is not current/reproducible here:** #5 (unsupported PUT is asserted as 405); #16 and #21 (both guidance strings are asserted in rendered pages); #20 (unsupported itinerary POST is asserted as 405); #27 (unknown-cargo `Http404` detail is asserted). These assertions are in `tests/booking/interfaces/test_route_selection.py`.
- The supplied survivor report is from 2026-11-07. The current mutation command did not regenerate it because no mutable code was changed.

### Remaining
- [ ] Restore a checkout/base where BK-05F production changes are present relative to the profile's `origin/main`, then rerun the exact changed-code mutation command and reconcile a fresh survivor report.
- [ ] If the verified score is below 0.8, add interface coverage for any genuine user-visible survivor or document an equivalent diff in the return.

### Decisions made
- Did not make an artificial production edit just to trigger changed-code mutation; the current profile command has no mutable code to test.
- Did not add tests for the five diffs already asserted by current interface tests or for internal exception details that do not alter the route-selection page.

### Blockers / questions
- The profile mutation gate cannot produce a score on this checkout: the BK-05F source is already present in `origin/main`. The required threshold is therefore unverified. Confirm the intended mutation comparison base or provide the BK-05F code delta before resuming.

### Failing commands
- No command failed; the changed-code mutation gate returned `n/a` rather than a score. See `.migration/runs/BK-05F/20261116T152853398139Z-mutation-changed.log`.

### Next step for the next session
Resolve the mutation-base mismatch first; then run the profile's exact changed-code mutation command and only change planned BK-05F files if a fresh survivor proves the need.
