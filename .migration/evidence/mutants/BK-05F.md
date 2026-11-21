# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `3e6a94a28aa0563b9ac475e7a4b4ef6821f8a516`): score 0.870, threshold 0.8, killed 47, survived 7. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:23 Mutant #4`

  ```diff
  @@ -20,7 +20,7 @@
       'No routes found that satisfy the route specification. '
       'Try setting an arrival deadline further into the future (a few weeks at least).'
   )
  -_CANDIDATE_SIGNING_SALT = 'booking.route_selection'
  +_CANDIDATE_SIGNING_SALT = 'XXbooking.route_selectionXX'
   def _candidate_token(tracking_id: TrackingId, itinerary: Itinerary) -> str:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:23 Mutant #5`

  ```diff
  @@ -20,7 +20,7 @@
       'No routes found that satisfy the route specification. '
       'Try setting an arrival deadline further into the future (a few weeks at least).'
   )
  -_CANDIDATE_SIGNING_SALT = 'booking.route_selection'
  +_CANDIDATE_SIGNING_SALT = None
   def _candidate_token(tracking_id: TrackingId, itinerary: Itinerary) -> str:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:49 Mutant #19`

  ```diff
  @@ -46,7 +46,7 @@
   def _selected_itinerary(token: str, tracking_id: TrackingId) -> Itinerary:
       payload = signing.loads(token, salt=_CANDIDATE_SIGNING_SALT)
  -    if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id.value:
  +    if not isinstance(payload, dict) and payload.get('tracking_id') != tracking_id.value:
           raise ValueError('The route selection does not match this cargo.')
       try:
           legs = tuple(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:50 Mutant #20`

  ```diff
  @@ -47,7 +47,7 @@
   def _selected_itinerary(token: str, tracking_id: TrackingId) -> Itinerary:
       payload = signing.loads(token, salt=_CANDIDATE_SIGNING_SALT)
       if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id.value:
  -        raise ValueError('The route selection does not match this cargo.')
  +        raise ValueError('XXThe route selection does not match this cargo.XX')
       try:
           legs = tuple(
               Leg(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:64 Mutant #30`

  ```diff
  @@ -61,7 +61,7 @@
           )
           return Itinerary(legs)
       except (KeyError, TypeError, ValueError) as error:
  -        raise ValueError('The route selection is invalid.') from error
  +        raise ValueError('XXThe route selection is invalid.XX') from error
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:77 Mutant #34`

  ```diff
  @@ -74,7 +74,7 @@
           cargo_id = TrackingId(tracking_id)
           cargo = cargo_dashboard.get_cargo_details(cargo_id)
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {cargo_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {cargo_id} not found.XX')
           if request.method == 'POST':
               try:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:82 Mutant #38`

  ```diff
  @@ -79,7 +79,7 @@
           if request.method == 'POST':
               try:
                   itinerary = _selected_itinerary(
  -                    request.POST.get('candidate_token', ''),
  +                    request.POST.get('candidate_token', 'XXXX'),
                       cargo_id,
                   )
               except (signing.BadSignature, ValueError):
  ```

