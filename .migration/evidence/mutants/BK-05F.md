# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `a135db8cd96803a5692cc2c30e5842fe1c87893c`): score 0.937, threshold 0.8, killed 59, survived 4. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:20 Mutant #1`

  ```diff
  @@ -17,7 +17,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'cargotracker.booking.route_selection'
  +_CANDIDATE_SALT = 'XXcargotracker.booking.route_selectionXX'
   _ROUTE_NO_CANDIDATES = (
       'No routes found that satisfy the route specification. '
       'Try setting an arrival deadline further into the future.'
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:20 Mutant #2`

  ```diff
  @@ -17,7 +17,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'cargotracker.booking.route_selection'
  +_CANDIDATE_SALT = None
   _ROUTE_NO_CANDIDATES = (
       'No routes found that satisfy the route specification. '
       'Try setting an arrival deadline further into the future.'
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:114 Mutant #44`

  ```diff
  @@ -111,7 +111,7 @@
               ],
           },
           salt=_CANDIDATE_SALT,
  -        compress=True,
  +        compress=False,
       )
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:127 Mutant #55`

  ```diff
  @@ -124,7 +124,7 @@
           if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id:
               return None
           leg_data = payload.get('legs')
  -        if not isinstance(leg_data, list) or not leg_data:
  +        if not isinstance(leg_data, list) and not leg_data:
               return None
           legs = [
               Leg(
  ```

