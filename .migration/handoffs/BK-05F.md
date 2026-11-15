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

## Handoff — afs-specialist-migrator · 2026-11-15T07:23:01Z
**State:** blocked · **Branch / PR:** `copilot/bk-05f-continue-changed-code-mutation` (eval checkout) / intended `copilot/bk-05f-build-route-selection-itinerary-screens` · https://github.com/martins-vds/ai-factory-pilot-target/pull/394 · **Last commit:** f8d55e7

### Done
- Setup passed: source SHA `f3beacf78de4f6d34edc4971ac87e38a5c6fe59d` is read-only and ignored, target ancestry is complete, migration validation and inputs passed, DB service is healthy, and Python 3.13.18 matches the profile.
- Read ticket #293 and confirmed its only application/test scope is `src/cargotracker/booking/interfaces/route_selection/views.py`, `templates/booking/route_selection/`, and `tests/booking/interfaces/test_route_selection.py`.
- The latest completed mutation evidence remains 0.790 (49 killed, 13 survived) in `.migration/evidence/mutants/BK-05F.md`. The required profile command was started through `afs-run`, but its workers targeted unrelated files and it was interrupted before producing an `AFS-RESULT`; it is not gate evidence. Log: `.migration/runs/BK-05F/20261115T071140510172Z-mutation-changed.log`.
- No application or test files were changed.

### Remaining
- [ ] Restore or provide the correct BK-05F base ref/checkout, then rerun the exact profile mutation command first.
- [ ] Resolve the genuine test gaps below and verify survivors that conflict with existing interface assertions against the correctly scoped run.
- [ ] Run every profile gate through `afs-run`, run CodeQL, update evidence/return, and validate `.migration`.

### Decisions made
- Stopped instead of changing files outside BK-05F scope or altering the profile gate command.

### Blockers / questions
- The eval checkout is on `copilot/bk-05f-continue-changed-code-mutation`; it does not contain `origin/copilot/bk-05f-build-route-selection-itinerary-screens`.
- The prescribed `--changed-since origin/main` run selected `src/cargotracker/cargo/domain/delivery.py`, `src/cargotracker/data_migration/loader.py`, `src/cargotracker/cargo/application/sample_data.py`, and `src/cargotracker/handling/application/process_registration_attempt.py`. None is in BK-05F's approved file list. The correct base/ref must be made available before mutation can validate this ticket.

### Failing commands
- `rtk .migration/harness/tools/afs-run --ticket BK-05F --name mutation-changed -- python .migration/harness/tools/afs-mutation --changed-since origin/main` → interrupted before completion (no exit/result); see `.migration/runs/BK-05F/20261115T071140510172Z-mutation-changed.log`.

### Survivor classifications from `.migration/evidence/mutants/BK-05F.md`

| Mutant | Diff | Classification |
|---|---|---|
| #1 | `_CANDIDATE_SALT = 'booking.route_selection'` → `_CANDIDATE_SALT = 'XXbooking.route_selectionXX'` | Missing interface test: submit a candidate signed with the stable, previously issued salt and assert assignment redirects to the details page. |
| #2 | `_CANDIDATE_SALT = 'booking.route_selection'` → `_CANDIDATE_SALT = None` | Missing interface test: same stable-salt compatibility assertion as #1. |
| #5 | `@require_http_methods(['GET', 'POST'])` → removed | Test-selection anomaly: `test_route_screens_reject_unsupported_http_methods` already expects 405 for PUT; verify the test is selected and executed after the correct base is available. Not equivalent. |
| #10 | `raise Http404(f'Cargo with tracking ID {tracking_id} not found.')` → `raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')` | Equivalent at the UI boundary: response remains the same 404 page; only the internal exception detail changes. |
| #13 | `raise Http404('The selected route no longer satisfies the route specification.')` → `raise Http404('XXThe selected route no longer satisfies the route specification.XX')` | Equivalent at the UI boundary: assignment remains rejected with 404; only internal exception detail changes. |
| #14 | `quote(tracking_id, safe="")` → `quote(tracking_id, safe="XXXX")` | Equivalent: `X` is an unreserved character which `urllib.parse.quote` leaves unescaped regardless of `safe`. |
| #16 | `'Try setting an arrival deadline further into the future.'` → `'XXTry setting an arrival deadline further into the future.XX'` | Test-selection anomaly: the current empty-state interface test already asserts the exact visible guidance; verify that assertion is selected/executed on the correct base. Not equivalent. |
| #20 | `@require_http_methods(['GET'])` → removed | Test-selection anomaly: the current unsupported-method interface test already expects 405 for POST; verify it is selected/executed on the correct base. Not equivalent. |
| #21 | `'Try setting the arrival deadline further into the future (a few weeks at least).'` → `'XXTry setting the arrival deadline further into the future (a few weeks at least).XX'` | Test-selection anomaly: the current empty-state interface test already asserts the exact visible guidance; verify that assertion is selected/executed on the correct base. Not equivalent. |
| #27 | `raise Http404(f'Cargo with tracking ID {tracking_id} not found.')` → `raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')` | Equivalent at the UI boundary: the response remains the same 404 page; only internal exception detail changes. |
| #40 | `request.POST.get('candidate', '')` → `request.POST.get('candidate', 'XXXX')` | Equivalent: both missing-field defaults fail signature validation and produce the same 404 response. |
| #44 | `raise BadSignature('Candidate belongs to another cargo.')` → `raise BadSignature('XXCandidate belongs to another cargo.XX')` | Equivalent: the exception is caught and normalized to the same `Http404` response. |
| #46 | `raise Http404('The selected route is invalid.')` → `raise Http404('XXThe selected route is invalid.XX')` | Equivalent at the UI boundary: response remains the same 404 page; only internal exception detail changes. |

### Next step for the next session
Make the correct BK-05F base ref available in this checkout (or resume in the matching target checkout), then rerun the profile's exact changed-code mutation command. Do not edit the unrelated files selected by the interrupted run.
