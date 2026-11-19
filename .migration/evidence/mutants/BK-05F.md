# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `8e683c5e2b82c5f52930c14332316a662734c1e8`): score 0.898, threshold 0.8, killed 44, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:25 Mutant #1`

  ```diff
  @@ -22,7 +22,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_TOKEN_SALT = 'booking.route-selection'
  +_TOKEN_SALT = 'XXbooking.route-selectionXX'
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:25 Mutant #2`

  ```diff
  @@ -22,7 +22,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_TOKEN_SALT = 'booking.route-selection'
  +_TOKEN_SALT = None
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:47 Mutant #15`

  ```diff
  @@ -44,7 +44,7 @@
           if request.method == 'POST':
               try:
                   itinerary = _itinerary_from_token(
  -                    request.POST.get('candidate_token', ''),
  +                    request.POST.get('candidate_token', 'XXXX'),
                       cargo_tracking_id,
                   )
               except (signing.BadSignature, KeyError, TypeError, ValueError):
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:51 Mutant #17`

  ```diff
  @@ -48,7 +48,7 @@
                       cargo_tracking_id,
                   )
               except (signing.BadSignature, KeyError, TypeError, ValueError):
  -                return HttpResponseBadRequest('Invalid route selection.')
  +                return HttpResponseBadRequest('XXInvalid route selection.XX')
               cargo_routing.assign_route(cargo_tracking_id, itinerary)
               return redirect(f'/admin/cargo/{tracking_id}/')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:97 Mutant #41`

  ```diff
  @@ -94,7 +94,7 @@
   def _itinerary_from_token(token: str, tracking_id: TrackingId) -> Itinerary:
       data = signing.loads(token, salt=_TOKEN_SALT)
       if not isinstance(data, dict) or data.get('tracking_id') != tracking_id.value:
  -        raise signing.BadSignature('The route selection does not match this cargo.')
  +        raise signing.BadSignature('XXThe route selection does not match this cargo.XX')
       return Itinerary(
           tuple(
               Leg(
  ```

