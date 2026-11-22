# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `4fe5d83ebcbf91da9bca259bf940f1d97b1a6483`): score 0.857, threshold 0.8, killed 54, survived 9. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:22 Mutant #1`

  ```diff
  @@ -19,7 +19,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'booking.route_selection'
  +_CANDIDATE_SALT = 'XXbooking.route_selectionXX'
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:22 Mutant #2`

  ```diff
  @@ -19,7 +19,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'booking.route_selection'
  +_CANDIDATE_SALT = None
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:34 Mutant #10`

  ```diff
  @@ -31,7 +31,7 @@
           if request.method == 'POST':
               cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
               if cargo is None:
  -                raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +                raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
               itinerary = _selected_itinerary(request, tracking_id)
               if not cargo.route_specification.is_satisfied_by(itinerary):
                   raise Http404('The selected route no longer satisfies the route specification.')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:37 Mutant #13`

  ```diff
  @@ -34,7 +34,7 @@
                   raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
               itinerary = _selected_itinerary(request, tracking_id)
               if not cargo.route_specification.is_satisfied_by(itinerary):
  -                raise Http404('The selected route no longer satisfies the route specification.')
  +                raise Http404('XXThe selected route no longer satisfies the route specification.XX')
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
               tracking_id_segment = quote(tracking_id, safe='')
               return redirect(f'/admin/cargo/{tracking_id_segment}/')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:39 Mutant #14`

  ```diff
  @@ -36,7 +36,7 @@
               if not cargo.route_specification.is_satisfied_by(itinerary):
                   raise Http404('The selected route no longer satisfies the route specification.')
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
  -            tracking_id_segment = quote(tracking_id, safe='')
  +            tracking_id_segment = quote(tracking_id, safe='XXXX')
               return redirect(f'/admin/cargo/{tracking_id_segment}/')
           context = _selection_context(
               cargo_routing,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:71 Mutant #28`

  ```diff
  @@ -68,7 +68,7 @@
       tracking_id = TrackingId(tracking_id_value)
       cargo = cargo_dashboard.get_cargo_details(tracking_id)
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       itineraries = cargo_routing.route_candidates(tracking_id)
       return {
           'cargo': cargo,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:96 Mutant #41`

  ```diff
  @@ -93,7 +93,7 @@
   def _selected_itinerary(request: HttpRequest, tracking_id: str) -> Itinerary:
       try:
  -        candidate = signing.loads(request.POST.get('candidate', ''), salt=_CANDIDATE_SALT)
  +        candidate = signing.loads(request.POST.get('candidate', 'XXXX'), salt=_CANDIDATE_SALT)
           if candidate['tracking_id'] != tracking_id:
               raise BadSignature('Candidate belongs to another cargo.')
           return _deserialize_itinerary(candidate['legs'])
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:98 Mutant #45`

  ```diff
  @@ -95,7 +95,7 @@
       try:
           candidate = signing.loads(request.POST.get('candidate', ''), salt=_CANDIDATE_SALT)
           if candidate['tracking_id'] != tracking_id:
  -            raise BadSignature('Candidate belongs to another cargo.')
  +            raise BadSignature('XXCandidate belongs to another cargo.XX')
           return _deserialize_itinerary(candidate['legs'])
       except (BadSignature, KeyError, TypeError, ValueError) as error:
           raise Http404('The selected route is invalid.') from error
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:101 Mutant #47`

  ```diff
  @@ -98,7 +98,7 @@
               raise BadSignature('Candidate belongs to another cargo.')
           return _deserialize_itinerary(candidate['legs'])
       except (BadSignature, KeyError, TypeError, ValueError) as error:
  -        raise Http404('The selected route is invalid.') from error
  +        raise Http404('XXThe selected route is invalid.XX') from error
   def _serialize_itinerary(itinerary: Itinerary) -> list[dict]:
  ```

