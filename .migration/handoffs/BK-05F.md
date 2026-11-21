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

## Handoff — afs-migrator · 2026-11-21T21:00:18Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-fix-changed-code-mutation-828c2afa-f9db-4312-b612-030a31eeb5b1` / https://github.com/martins-vds/ai-factory-eval/pull/2170 · **Last commit:** d59fe4e5

### Done
- Setup passed; source SHA is `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d`, read-only and ignored.
- The initial changed-code mutation run correctly reported `n/a` because the checkout had no mutable delta from `origin/main`. After the planned view change, the final profile mutation gate passed at 0.869 (53 killed, 8 survived); see `.migration/runs/BK-05F/20261121T205334460259Z-mutation-changed-final.log`.
- The revised complete-message UI assertions killed the visible guidance mutants. The focused interface test and full suite passed (468 tests); all build, idiom, and CRAP gates passed. The committed journal is `.migration/evidence/runs/BK-05F.md`.
- The return records the original and final mutant classifications in `.migration/returns/BK-05F.afs-migrator.yaml`. CodeQL was skipped because all code changes were assessed as trivial.

### Remaining
- [ ] Obtain operator approval to extend BK-05F scope for the rule inventory/check required by `afs-migrator`.
- [ ] Under the approved scope, add `rules` or `no_rules` to the four capability ledgers and add the direct-use-case tests required for any rules.
- [ ] Update the return and clear the handoff only after `.migration/harness/tools/validate.py .migration` passes.

### Decisions made
- Removed the redundant `''` default for a missing candidate token; `signing.loads(None)` still maps through the existing exception handler to the same invalid-candidate 404.
- The 8 final surviving mutants are documented as equivalent in the return: internally consistent token salt changes, non-rendered 404 exception details, and a `quote` safe-set change that does not alter output.

### Blockers / questions
- The stop rule fired: `.migration/plan/booking.tickets.yaml` scopes BK-05F to `src/cargotracker/booking/interfaces/route_selection/views.py`, `templates/booking/route_selection/`, and `tests/booking/interfaces/test_route_selection.py`. Final validation for an `afs-migrator` return requires rule/no-rule entries for `booking.routing-chain`, `booking.screen-route`, `booking.screen-select-itinerary`, and `booking.routing-assign`, plus direct use-case tests. It flagged the ledger files `.migration/ledger/booking.routing-chain.yaml`, `.migration/ledger/booking.screen-route.yaml`, `.migration/ledger/booking.screen-select-itinerary.yaml`, `.migration/ledger/booking.routing-assign.yaml`; the likely application-test path is `tests/booking/application/test_routing.py`. These paths are outside BK-05F's approved file list. Do not edit them until the operator approves an extension or a new ticket.

### Failing commands
- `.migration/harness/tools/afs-run --ticket BK-05F --name validate-scope-blocker -- python .migration/harness/tools/validate.py .migration` → exit 1, see `.migration/runs/BK-05F/20261121T210007337819Z-validate-scope-blocker.log` (5 rule-inventory errors described above).
- `.migration/harness/tools/afs-run --ticket BK-05F --name guidance-assertion-red -- pytest -q tests/booking/interfaces/test_route_selection.py::test_route_screens_explain_when_no_candidates_satisfy_the_deadline` → exit 1 as expected while the source was temporarily set to the #16 `XX…XX` mutant; the final UI test passes on the correct source.

### Next step for the next session
Ask the operator to authorize the four ledger files and direct application tests (or create a scoped follow-up ticket); then complete the rule inventory, validate the return, and only then close the handoff.
