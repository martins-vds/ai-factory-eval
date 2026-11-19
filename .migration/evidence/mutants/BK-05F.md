# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `5ec4a4b699c3194294e74243c50dea12b0e76163`): score 0.702, threshold 0.8, killed 40, survived 17. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:63 Mutant #20`

  ```diff
  @@ -60,7 +60,7 @@
       ) -> HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           session_key = f'booking_route_candidates:{cargo.tracking_id.value}'
           candidates = ()
  ```

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

- `src/cargotracker/booking/interfaces/route_selection/views.py:67 Mutant #24`

  ```diff
  @@ -64,7 +64,7 @@
           session_key = f'booking_route_candidates:{cargo.tracking_id.value}'
           candidates = ()
  -        selection_error = ''
  +        selection_error = 'XXXX'
           if request.method == 'POST':
               stored_candidates = request.session.get(session_key)
               try:
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

- `src/cargotracker/booking/interfaces/route_selection/views.py:73 Mutant #30`

  ```diff
  @@ -70,7 +70,7 @@
               try:
                   candidates = tuple(_deserialize_itinerary(legs) for legs in stored_candidates)
               except (KeyError, TypeError, ValueError):
  -                candidates = ()
  +                candidates = None
               try:
                   candidate_index = int(request.POST.get('candidate_index', ''))
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:76 Mutant #32`

  ```diff
  @@ -73,7 +73,7 @@
                   candidates = ()
               try:
  -                candidate_index = int(request.POST.get('candidate_index', ''))
  +                candidate_index = int(request.POST.get('candidate_index', 'XXXX'))
               except ValueError:
                   candidate_index = -1
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:78 Mutant #34`

  ```diff
  @@ -75,7 +75,7 @@
               try:
                   candidate_index = int(request.POST.get('candidate_index', ''))
               except ValueError:
  -                candidate_index = -1
  +                candidate_index = +1
               if 0 <= candidate_index < len(candidates):
                   cargo_routing.assign_route(cargo.tracking_id, candidates[candidate_index])
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:78 Mutant #35`

  ```diff
  @@ -75,7 +75,7 @@
               try:
                   candidate_index = int(request.POST.get('candidate_index', ''))
               except ValueError:
  -                candidate_index = -1
  +                candidate_index = -2
               if 0 <= candidate_index < len(candidates):
                   cargo_routing.assign_route(cargo.tracking_id, candidates[candidate_index])
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:78 Mutant #36`

  ```diff
  @@ -75,7 +75,7 @@
               try:
                   candidate_index = int(request.POST.get('candidate_index', ''))
               except ValueError:
  -                candidate_index = -1
  +                candidate_index = None
               if 0 <= candidate_index < len(candidates):
                   cargo_routing.assign_route(cargo.tracking_id, candidates[candidate_index])
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:85 Mutant #41`

  ```diff
  @@ -82,7 +82,7 @@
                   del request.session[session_key]
                   return redirect(f'/admin/cargo/{cargo.tracking_id.value}/')
  -            selection_error = 'Select one of the available itineraries.'
  +            selection_error = 'XXSelect one of the available itineraries.XX'
               if stored_candidates is None:
                   candidates = cargo_routing.route_candidates(cargo.tracking_id)
                   request.session[session_key] = [
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:86 Mutant #43`

  ```diff
  @@ -83,7 +83,7 @@
                   return redirect(f'/admin/cargo/{cargo.tracking_id.value}/')
               selection_error = 'Select one of the available itineraries.'
  -            if stored_candidates is None:
  +            if stored_candidates is not None:
                   candidates = cargo_routing.route_candidates(cargo.tracking_id)
                   request.session[session_key] = [
                       _serialize_itinerary(candidate) for candidate in candidates
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:87 Mutant #44`

  ```diff
  @@ -84,7 +84,7 @@
               selection_error = 'Select one of the available itineraries.'
               if stored_candidates is None:
  -                candidates = cargo_routing.route_candidates(cargo.tracking_id)
  +                candidates = None
                   request.session[session_key] = [
                       _serialize_itinerary(candidate) for candidate in candidates
                   ]
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:90 Mutant #45`

  ```diff
  @@ -85,9 +85,7 @@
               selection_error = 'Select one of the available itineraries.'
               if stored_candidates is None:
                   candidates = cargo_routing.route_candidates(cargo.tracking_id)
  -                request.session[session_key] = [
  -                    _serialize_itinerary(candidate) for candidate in candidates
  -                ]
  +                request.session[session_key] = None
           else:
               candidates = cargo_routing.route_candidates(cargo.tracking_id)
               request.session[session_key] = [
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:101 Mutant #48`

  ```diff
  @@ -98,7 +98,7 @@
               request,
               template_name,
               {
  -                'cargo': cargo,
  +                'XXcargoXX': cargo,
                   'candidates': candidates,
                   'candidate_count': len(candidates),
                   'selection_error': selection_error,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:115 Mutant #55`

  ```diff
  @@ -112,7 +112,7 @@
               request,
               tracking_id,
               'booking/route_selection/route.html',
  -            'Route Cargo {tracking_id}',
  +            'XXRoute Cargo {tracking_id}XX',
           )
       def itinerary_selection(request: HttpRequest, tracking_id: str) -> HttpResponse:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:123 Mutant #57`

  ```diff
  @@ -120,7 +120,7 @@
               request,
               tracking_id,
               'booking/route_selection/itineraries.html',
  -            'Select an itinerary for cargo {tracking_id}',
  +            'XXSelect an itinerary for cargo {tracking_id}XX',
           )
       return route_selection, itinerary_selection
  ```

