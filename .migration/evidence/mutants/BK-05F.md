# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `e2ecfc53f83d7ede9376c72b89117d8f03ac2f86`): score 0.867, threshold 0.8, killed 26, survived 4. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:39 Mutant #8`

  ```diff
  @@ -36,7 +36,7 @@
               request,
               template,
               {
  -                'cargo': cargo,
  +                'XXcargoXX': cargo,
                   'candidates': candidates,
                   'candidate_count': len(candidates),
               },
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:66 Mutant #20`

  ```diff
  @@ -63,7 +63,7 @@
               return redirect(f'/admin/cargo/{canonical_tracking_id}/route/')
           candidates = cargo_routing.route_candidates(TrackingId(tracking_id))
           try:
  -            candidate_index = int(request.POST.get('candidate', ''))
  +            candidate_index = int(request.POST.get('candidate', 'XXXX'))
           except (TypeError, ValueError):
               candidate_index = -1
           if candidate_index < 0 or candidate_index >= len(candidates):
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:68 Mutant #22`

  ```diff
  @@ -65,7 +65,7 @@
           try:
               candidate_index = int(request.POST.get('candidate', ''))
           except (TypeError, ValueError):
  -            candidate_index = -1
  +            candidate_index = +1
           if candidate_index < 0 or candidate_index >= len(candidates):
               raise Http404('No route candidate was selected.')
           cargo_routing.assign_route(TrackingId(tracking_id), candidates[candidate_index])
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:68 Mutant #23`

  ```diff
  @@ -65,7 +65,7 @@
           try:
               candidate_index = int(request.POST.get('candidate', ''))
           except (TypeError, ValueError):
  -            candidate_index = -1
  +            candidate_index = -2
           if candidate_index < 0 or candidate_index >= len(candidates):
               raise Http404('No route candidate was selected.')
           cargo_routing.assign_route(TrackingId(tracking_id), candidates[candidate_index])
  ```

