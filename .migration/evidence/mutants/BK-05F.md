# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `93a9ad8872675fb2aa770724a314257adcf39f1e`): score 0.857, threshold 0.8, killed 48, survived 8. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:20 Mutant #1`

  ```diff
  @@ -17,7 +17,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_ITINERARY_SALT = 'cargotracker.booking.route-selection'
  +_ITINERARY_SALT = 'XXcargotracker.booking.route-selectionXX'
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:20 Mutant #2`

  ```diff
  @@ -17,7 +17,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_ITINERARY_SALT = 'cargotracker.booking.route-selection'
  +_ITINERARY_SALT = None
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:40 Mutant #8`

  ```diff
  @@ -37,7 +37,7 @@
                       request,
                       cargo_routing,
                       cargo,
  -                    title='Route Cargo',
  +                    title='XXRoute CargoXX',
                       no_routes_guidance=('Try setting an arrival deadline further into the future.'),
                       error='Select a route shown on this page.',
                       status=400,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:41 Mutant #9`

  ```diff
  @@ -38,7 +38,7 @@
                       cargo_routing,
                       cargo,
                       title='Route Cargo',
  -                    no_routes_guidance=('Try setting an arrival deadline further into the future.'),
  +                    no_routes_guidance=('XXTry setting an arrival deadline further into the future.XX'),
                       error='Select a route shown on this page.',
                       status=400,
                   )
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:42 Mutant #10`

  ```diff
  @@ -39,7 +39,7 @@
                       cargo,
                       title='Route Cargo',
                       no_routes_guidance=('Try setting an arrival deadline further into the future.'),
  -                    error='Select a route shown on this page.',
  +                    error='XXSelect a route shown on this page.XX',
                       status=400,
                   )
               cargo_routing.assign_route(cargo.tracking_id, itinerary)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:52 Mutant #14`

  ```diff
  @@ -49,7 +49,7 @@
               cargo_routing,
               cargo,
               title='Route Cargo',
  -            no_routes_guidance='Try setting an arrival deadline further into the future.',
  +            no_routes_guidance='XXTry setting an arrival deadline further into the future.XX',
           )
       def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:63 Mutant #17`

  ```diff
  @@ -60,7 +60,7 @@
               cargo,
               title='Select Itinerary',
               no_routes_guidance=(
  -                'Try setting an arrival deadline further into the future (a few weeks at least).'
  +                'XXTry setting an arrival deadline further into the future (a few weeks at least).XX'
               ),
           )
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:131 Mutant #49`

  ```diff
  @@ -128,7 +128,7 @@
       if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id.value:
           raise ValueError
       legs = payload.get('legs')
  -    if not isinstance(legs, list) or not legs:
  +    if not isinstance(legs, list) and not legs:
           raise ValueError
       return Itinerary(
           tuple(
  ```

