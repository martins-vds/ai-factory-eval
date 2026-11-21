# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `36fae5a689c9209c673e36ecb81a55398131911e`): score 0.906, threshold 0.8, killed 48, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:49 Mutant #16`

  ```diff
  @@ -46,7 +46,7 @@
   def _itinerary_from_token(token: str, tracking_id: TrackingId) -> Itinerary:
       payload = signing.loads(token)
       if payload['tracking_id'] != tracking_id.value or not payload['legs']:
  -        raise signing.BadSignature('Invalid itinerary selection')
  +        raise signing.BadSignature('XXInvalid itinerary selectionXX')
       return Itinerary(
           tuple(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:87 Mutant #33`

  ```diff
  @@ -84,7 +84,7 @@
           if request.method == 'POST':
               cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
               if cargo is None:
  -                raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +                raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
               try:
                   itinerary = _itinerary_from_token(
                       request.POST.get('itinerary_token', ''),
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:90 Mutant #35`

  ```diff
  @@ -87,7 +87,7 @@
                   raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
               try:
                   itinerary = _itinerary_from_token(
  -                    request.POST.get('itinerary_token', ''),
  +                    request.POST.get('itinerary_token', 'XXXX'),
                       cargo.tracking_id,
                   )
               except (signing.BadSignature, KeyError, TypeError, ValueError):
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:94 Mutant #37`

  ```diff
  @@ -91,7 +91,7 @@
                       cargo.tracking_id,
                   )
               except (signing.BadSignature, KeyError, TypeError, ValueError):
  -                return HttpResponseBadRequest('Invalid itinerary selection.')
  +                return HttpResponseBadRequest('XXInvalid itinerary selection.XX')
               cargo_routing.assign_route(cargo.tracking_id, itinerary)
               return redirect(f'/admin/cargo/{cargo.tracking_id.value}/')
           if request.method != 'GET':
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:120 Mutant #47`

  ```diff
  @@ -117,7 +117,7 @@
       tracking = TrackingId(tracking_id)
       cargo = cargo_dashboard.get_cargo_details(tracking)
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       itineraries = cargo_routing.route_candidates(tracking)
       route_candidates = [
           {'itinerary': itinerary, 'token': _candidate_token(cargo.tracking_id, itinerary)}
  ```
