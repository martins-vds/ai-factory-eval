# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `efc825d24a5c7a60f0623774c8ec2f224357668f`): score 0.897, threshold 0.8, killed 52, survived 6. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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
               return redirect(f'/admin/cargo/{quote(tracking_id, safe="")}/')
           context = _selection_context(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:39 Mutant #14`

  ```diff
  @@ -36,7 +36,7 @@
               if not cargo.route_specification.is_satisfied_by(itinerary):
                   raise Http404('The selected route no longer satisfies the route specification.')
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
  -            return redirect(f'/admin/cargo/{quote(tracking_id, safe="")}/')
  +            return redirect(f'/admin/cargo/{quote(tracking_id, safe="XXXX")}/')
           context = _selection_context(
               cargo_routing,
               cargo_dashboard,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:63 Mutant #25`

  ```diff
  @@ -60,7 +60,7 @@
       tracking_id = TrackingId(tracking_id_value)
       cargo = cargo_dashboard.get_cargo_details(tracking_id)
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       itineraries = cargo_routing.route_candidates(tracking_id)
       return {
           'cargo': cargo,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:87 Mutant #37`

  ```diff
  @@ -84,7 +84,7 @@
   def _selected_itinerary(request: HttpRequest, tracking_id: str) -> Itinerary:
       try:
  -        candidate = signing.loads(request.POST.get('candidate', ''), salt=_CANDIDATE_SALT)
  +        candidate = signing.loads(request.POST.get('candidate', 'XXXX'), salt=_CANDIDATE_SALT)
           if candidate['tracking_id'] != tracking_id:
               raise BadSignature
           return _deserialize_itinerary(candidate['legs'])
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:92 Mutant #42`

  ```diff
  @@ -89,7 +89,7 @@
               raise BadSignature
           return _deserialize_itinerary(candidate['legs'])
       except (BadSignature, KeyError, TypeError, ValueError) as error:
  -        raise Http404('The selected route is invalid.') from error
  +        raise Http404('XXThe selected route is invalid.XX') from error
   def _serialize_itinerary(itinerary: Itinerary) -> list[dict]:
  ```

