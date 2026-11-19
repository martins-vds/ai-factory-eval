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

## Handoff — afs-migrator · 2026-11-19T22:28:08Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-classify-survivor-diffs` / https://github.com/martins-vds/ai-factory-eval/pull/1609 · **Last commit:** 70805ac0

### Done
- Setup passed; source SHA is `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`.
- Changed-code mutation passed at 0.887 (55 killed, 7 survived); build, idiom, behavior (470 tests), and CRAP (26/30) passed through `afs-run`. Journal: `.migration/evidence/runs/BK-05F.md`.
- Added interface coverage for default-salt and cross-cargo candidate rejection, tightened exact empty-state and unknown-cargo assertions, and updated the relevant ledger evidence.
- CodeQL found no alerts. The seven surviving mutants and their classifications are recorded in `.migration/returns/BK-05F.afs-migrator.yaml`.

### Remaining
- [ ] Resolve the rule-layer issue below within authorized scope, or obtain approval for a separate follow-up ticket.
- [ ] After that decision, update the return and rerun validation and any affected gates.

### Decisions made
- No changes were made outside BK-05F's planned files.
- The candidate-token salt literal, 404 detail text, missing-token default, and `quote(..., safe="XXXX")` survivors are classified as behavior-equivalent in the return.

### Blockers / questions
- The route-selection POST view refuses an itinerary when it no longer satisfies the cargo's current route specification. Migrator verification requires a direct use-case test proving this rule is enforced by `CargoRouting.assign_route`, but the use case currently accepts such an itinerary and records it as misrouted.
- The BK-05F plan does not include `src/cargotracker/booking/application/routing.py` or `tests/booking/application/test_routing.py`. Do not modify those paths without a scope extension or separate ticket.

### Failing commands
- The two `route-guidance-mutant-red` and `itinerary-guidance-mutant-red` test probes intentionally failed against the corresponding `XX...XX` mutants; see `.migration/runs/BK-05F/20261119T220122855794Z-route-guidance-mutant-red.log` and `.migration/runs/BK-05F/20261119T220139175785Z-itinerary-guidance-mutant-red.log`.
- No final profile gate failed.

### Next step for the next session
Ask the coordinator/operator to authorize the application-layer route-specification rule and direct use-case test, or create a follow-up ticket for those out-of-scope files. Resume only after the scope decision.
