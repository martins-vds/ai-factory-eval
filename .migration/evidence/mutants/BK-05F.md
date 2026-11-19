# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `8e683c5e2b82c5f52930c14332316a662734c1e8`): score 0.900, threshold 0.8, killed 45, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:26 Mutant #1`

  ```diff
  @@ -23,7 +23,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_TOKEN_SALT = 'booking.route-selection'
  +_TOKEN_SALT = 'XXbooking.route-selectionXX'
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:26 Mutant #2`

  ```diff
  @@ -23,7 +23,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_TOKEN_SALT = 'booking.route-selection'
  +_TOKEN_SALT = None
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:48 Mutant #15`

  ```diff
  @@ -45,7 +45,7 @@
           if request.method == 'POST':
               try:
                   itinerary = _itinerary_from_token(
  -                    request.POST.get('candidate_token', ''),
  +                    request.POST.get('candidate_token', 'XXXX'),
                       cargo_tracking_id,
                   )
               except (signing.BadSignature, KeyError, TypeError, ValueError):
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:52 Mutant #17`

  ```diff
  @@ -49,7 +49,7 @@
                       cargo_tracking_id,
                   )
               except (signing.BadSignature, KeyError, TypeError, ValueError):
  -                return HttpResponseBadRequest('Invalid route selection.')
  +                return HttpResponseBadRequest('XXInvalid route selection.XX')
               cargo_routing.assign_route(cargo_tracking_id, itinerary)
               return redirect(
                   reverse('cargo-details', kwargs={'tracking_id': cargo.tracking_id.value})
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:100 Mutant #42`

  ```diff
  @@ -97,7 +97,7 @@
   def _itinerary_from_token(token: str, tracking_id: TrackingId) -> Itinerary:
       data = signing.loads(token, salt=_TOKEN_SALT)
       if not isinstance(data, dict) or data.get('tracking_id') != tracking_id.value:
  -        raise signing.BadSignature('The route selection does not match this cargo.')
  +        raise signing.BadSignature('XXThe route selection does not match this cargo.XX')
       return Itinerary(
           tuple(
               Leg(
  ```

