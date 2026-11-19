# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `5ec4a4b699c3194294e74243c50dea12b0e76163`): score 0.912, threshold 0.8, killed 52, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:65 Mutant #21`

  ```diff
  @@ -62,7 +62,7 @@
           if cargo is None:
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  -        session_key = f'booking_route_candidates:{cargo.tracking_id.value}'
  +        session_key = f'XXbooking_route_candidates:{cargo.tracking_id.value}XX'
           candidates = ()
           selection_error = ''
           if request.method == 'POST':
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:66 Mutant #23`

  ```diff
  @@ -63,7 +63,7 @@
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
           session_key = f'booking_route_candidates:{cargo.tracking_id.value}'
  -        candidates = ()
  +        candidates = None
           selection_error = ''
           if request.method == 'POST':
               stored_candidates = request.session.get(session_key)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:67 Mutant #25`

  ```diff
  @@ -64,7 +64,7 @@
           session_key = f'booking_route_candidates:{cargo.tracking_id.value}'
           candidates = ()
  -        selection_error = ''
  +        selection_error = None
           if request.method == 'POST':
               stored_candidates = request.session.get(session_key)
               try:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:86 Mutant #41`

  ```diff
  @@ -83,7 +83,7 @@
                   del request.session[session_key]
                   return redirect(f'/admin/cargo/{cargo.tracking_id.value}/')
  -            selection_error = 'Select one of the available itineraries.'
  +            selection_error = 'XXSelect one of the available itineraries.XX'
               if stored_candidates is None:
                   candidates = cargo_routing.route_candidates(cargo.tracking_id)
                   request.session[session_key] = [
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:102 Mutant #48`

  ```diff
  @@ -99,7 +99,7 @@
               request,
               template_name,
               {
  -                'cargo': cargo,
  +                'XXcargoXX': cargo,
                   'candidates': candidates,
                   'candidate_count': len(candidates),
                   'selection_error': selection_error,
  ```

