# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `3ef02a70b0e74c04018a87fea0aec3e1a8f1edf8`): score 0.839, threshold 0.8, killed 26, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:24 Mutant #5`

  ```diff
  @@ -21,7 +21,7 @@
           cargo = (
               cargo_dashboard.get_cargo_details(tracking)
               if cargo_dashboard is not None
  -            else getattr(cargo_routing, '_find_cargo', lambda _tracking: None)(tracking)
  +            else getattr(cargo_routing, '_find_cargo', lambda _tracking: 0)(tracking)
           )
           if cargo is None:
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:44 Mutant #18`

  ```diff
  @@ -41,7 +41,7 @@
           if request.method == 'POST':
               try:
  -                candidate_index = int(request.POST.get('candidate', ''))
  +                candidate_index = int(request.POST.get('candidate', 'XXXX'))
               except (TypeError, ValueError):
                   raise Http404('A valid route candidate is required.')
               if candidate_index < 0 or candidate_index >= len(candidates):
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:46 Mutant #20`

  ```diff
  @@ -43,7 +43,7 @@
               try:
                   candidate_index = int(request.POST.get('candidate', ''))
               except (TypeError, ValueError):
  -                raise Http404('A valid route candidate is required.')
  +                raise Http404('XXA valid route candidate is required.XX')
               if candidate_index < 0 or candidate_index >= len(candidates):
                   raise Http404('A valid route candidate is required.')
               cargo_routing.assign_route(tracking, candidates[candidate_index])
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:48 Mutant #25`

  ```diff
  @@ -45,7 +45,7 @@
               except (TypeError, ValueError):
                   raise Http404('A valid route candidate is required.')
               if candidate_index < 0 or candidate_index >= len(candidates):
  -                raise Http404('A valid route candidate is required.')
  +                raise Http404('XXA valid route candidate is required.XX')
               cargo_routing.assign_route(tracking, candidates[candidate_index])
               return redirect(f'/admin/cargo/{tracking_id}/')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:58 Mutant #30`

  ```diff
  @@ -55,7 +55,7 @@
               {
                   'tracking_id': tracking_id,
                   'candidates': candidates,
  -                'candidate_count': len(candidates),
  +                'XXcandidate_countXX': len(candidates),
               },
           )
  ```

