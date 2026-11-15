# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `origin/main`): score 0.855, threshold 0.8, killed 53, survived 9. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:31 Mutant #8`

  ```diff
  @@ -28,7 +28,7 @@
           if request.method == 'POST':
               cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
               if cargo is None:
  -                raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +                raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
               itinerary = _selected_itinerary(request, tracking_id)
               if not cargo.route_specification.is_satisfied_by(itinerary):
                   raise Http404('The selected route no longer satisfies the route specification.')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:34 Mutant #11`

  ```diff
  @@ -31,7 +31,7 @@
                   raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
               itinerary = _selected_itinerary(request, tracking_id)
               if not cargo.route_specification.is_satisfied_by(itinerary):
  -                raise Http404('The selected route no longer satisfies the route specification.')
  +                raise Http404('XXThe selected route no longer satisfies the route specification.XX')
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
               return redirect(f'/admin/cargo/{quote(tracking_id, safe="")}/')
           context = _selection_context(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:36 Mutant #12`

  ```diff
  @@ -33,7 +33,7 @@
               if not cargo.route_specification.is_satisfied_by(itinerary):
                   raise Http404('The selected route no longer satisfies the route specification.')
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
  -            return redirect(f'/admin/cargo/{quote(tracking_id, safe="")}/')
  +            return redirect(f'/admin/cargo/{quote(tracking_id, safe="XXXX")}/')
           context = _selection_context(
               cargo_routing,
               cargo_dashboard,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:41 Mutant #14`

  ```diff
  @@ -38,7 +38,7 @@
               cargo_routing,
               cargo_dashboard,
               tracking_id,
  -            'Try setting an arrival deadline further into the future.',
  +            'XXTry setting an arrival deadline further into the future.XX',
           )
           return render(request, 'booking/route_selection/route.html', context)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:51 Mutant #19`

  ```diff
  @@ -48,7 +48,7 @@
               cargo_routing,
               cargo_dashboard,
               tracking_id,
  -            'Try setting the arrival deadline further into the future (a few weeks at least).',
  +            'XXTry setting the arrival deadline further into the future (a few weeks at least).XX',
           )
           return render(request, 'booking/route_selection/select_itinerary.html', context)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:67 Mutant #25`

  ```diff
  @@ -64,7 +64,7 @@
       tracking_id = TrackingId(tracking_id_value)
       cargo = cargo_dashboard.get_cargo_details(tracking_id)
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       itineraries = cargo_routing.route_candidates(tracking_id)
       return {
           'cargo': cargo,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:92 Mutant #39`

  ```diff
  @@ -89,7 +89,7 @@
   def _selected_itinerary(request: HttpRequest, tracking_id: str) -> Itinerary:
       try:
  -        candidate = signing.loads(request.POST.get('candidate', ''), salt='booking.route_selection')
  +        candidate = signing.loads(request.POST.get('candidate', 'XXXX'), salt='booking.route_selection')
           if candidate['tracking_id'] != tracking_id:
               raise BadSignature('Candidate belongs to another cargo.')
           return _deserialize_itinerary(candidate['legs'])
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:94 Mutant #44`

  ```diff
  @@ -91,7 +91,7 @@
       try:
           candidate = signing.loads(request.POST.get('candidate', ''), salt='booking.route_selection')
           if candidate['tracking_id'] != tracking_id:
  -            raise BadSignature('Candidate belongs to another cargo.')
  +            raise BadSignature('XXCandidate belongs to another cargo.XX')
           return _deserialize_itinerary(candidate['legs'])
       except (BadSignature, KeyError, TypeError, ValueError) as error:
           raise Http404('The selected route is invalid.') from error
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:97 Mutant #46`

  ```diff
  @@ -94,7 +94,7 @@
               raise BadSignature('Candidate belongs to another cargo.')
           return _deserialize_itinerary(candidate['legs'])
       except (BadSignature, KeyError, TypeError, ValueError) as error:
  -        raise Http404('The selected route is invalid.') from error
  +        raise Http404('XXThe selected route is invalid.XX') from error
   def _serialize_itinerary(itinerary: Itinerary) -> list[dict]:
  ```

