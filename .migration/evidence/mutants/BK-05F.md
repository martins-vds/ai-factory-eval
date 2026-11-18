# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `origin/main`): score 0.887, threshold 0.8, killed 47, survived 6. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:25 Mutant #1`

  ```diff
  @@ -22,7 +22,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_ROUTE_SELECTION_SALT = 'cargotracker.booking.route-selection'
  +_ROUTE_SELECTION_SALT = 'XXcargotracker.booking.route-selectionXX'
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:25 Mutant #2`

  ```diff
  @@ -22,7 +22,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_ROUTE_SELECTION_SALT = 'cargotracker.booking.route-selection'
  +_ROUTE_SELECTION_SALT = None
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:72 Mutant #20`

  ```diff
  @@ -69,7 +69,7 @@
       cargo = cargo_dashboard.get_cargo_details(cargo_id)
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       candidates = cargo_routing.route_candidates(cargo_id)
       return render(
           request,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:109 Mutant #36`

  ```diff
  @@ -106,7 +106,7 @@
               ],
           },
           salt=_ROUTE_SELECTION_SALT,
  -        compress=True,
  +        compress=False,
       )
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:117 Mutant #38`

  ```diff
  @@ -114,7 +114,7 @@
       if not token:
           return None
       try:
  -        payload = signing.loads(token, salt=_ROUTE_SELECTION_SALT, max_age=3600)
  +        payload = signing.loads(token, salt=_ROUTE_SELECTION_SALT, max_age=3601)
           if payload['tracking_id'] != tracking_id:
               return None
           legs = payload['legs']
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:121 Mutant #46`

  ```diff
  @@ -118,7 +118,7 @@
           if payload['tracking_id'] != tracking_id:
               return None
           legs = payload['legs']
  -        if not isinstance(legs, list) or not legs:
  +        if not isinstance(legs, list) and not legs:
               return None
           return Itinerary(
               Leg(
  ```

