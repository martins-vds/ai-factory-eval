# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `93a9ad8872675fb2aa770724a314257adcf39f1e`): score 0.712, threshold 0.8, killed 42, survived 17. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

- `src/cargotracker/booking/interfaces/route_selection/views.py:32 Mutant #7`

  ```diff
  @@ -29,7 +29,7 @@
           if request.method == 'POST':
               try:
                   itinerary = _decode_itinerary(
  -                    request.POST.get('itinerary_token', ''),
  +                    request.POST.get('itinerary_token', 'XXXX'),
                       cargo.tracking_id,
                   )
               except (signing.BadSignature, KeyError, TypeError, ValueError):
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:40 Mutant #9`

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

- `src/cargotracker/booking/interfaces/route_selection/views.py:41 Mutant #10`

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

- `src/cargotracker/booking/interfaces/route_selection/views.py:42 Mutant #11`

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

- `src/cargotracker/booking/interfaces/route_selection/views.py:51 Mutant #14`

  ```diff
  @@ -48,7 +48,7 @@
               request,
               cargo_routing,
               cargo,
  -            title='Route Cargo',
  +            title='XXRoute CargoXX',
               no_routes_guidance='Try setting an arrival deadline further into the future.',
           )
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:52 Mutant #15`

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

- `src/cargotracker/booking/interfaces/route_selection/views.py:61 Mutant #17`

  ```diff
  @@ -58,7 +58,7 @@
               request,
               cargo_routing,
               cargo,
  -            title='Select Itinerary',
  +            title='XXSelect ItineraryXX',
               no_routes_guidance=(
                   'Try setting an arrival deadline further into the future (a few weeks at least).'
               ),
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:63 Mutant #18`

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

- `src/cargotracker/booking/interfaces/route_selection/views.py:73 Mutant #21`

  ```diff
  @@ -70,7 +70,7 @@
   def _get_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
       cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       return cargo
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:104 Mutant #29`

  ```diff
  @@ -101,7 +101,7 @@
           request,
           'booking/route_selection/route_selection.html',
           {
  -            'cargo': cargo,
  +            'XXcargoXX': cargo,
               'routes': routes,
               'title': title,
               'no_routes_guidance': no_routes_guidance,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:106 Mutant #31`

  ```diff
  @@ -103,7 +103,7 @@
           {
               'cargo': cargo,
               'routes': routes,
  -            'title': title,
  +            'XXtitleXX': title,
               'no_routes_guidance': no_routes_guidance,
               'error': error,
           },
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:128 Mutant #45`

  ```diff
  @@ -125,7 +125,7 @@
   def _decode_itinerary(token: str, tracking_id: TrackingId) -> Itinerary:
       payload = signing.loads(token, salt=_ITINERARY_SALT)
  -    if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id.value:
  +    if not isinstance(payload, dict) and payload.get('tracking_id') != tracking_id.value:
           raise ValueError('The selected itinerary does not belong to this cargo.')
       legs = payload.get('legs')
       if not isinstance(legs, list) or not legs:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:129 Mutant #46`

  ```diff
  @@ -126,7 +126,7 @@
   def _decode_itinerary(token: str, tracking_id: TrackingId) -> Itinerary:
       payload = signing.loads(token, salt=_ITINERARY_SALT)
       if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id.value:
  -        raise ValueError('The selected itinerary does not belong to this cargo.')
  +        raise ValueError('XXThe selected itinerary does not belong to this cargo.XX')
       legs = payload.get('legs')
       if not isinstance(legs, list) or not legs:
           raise ValueError('The selected itinerary has no legs.')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:131 Mutant #51`

  ```diff
  @@ -128,7 +128,7 @@
       if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id.value:
           raise ValueError('The selected itinerary does not belong to this cargo.')
       legs = payload.get('legs')
  -    if not isinstance(legs, list) or not legs:
  +    if not isinstance(legs, list) and not legs:
           raise ValueError('The selected itinerary has no legs.')
       return Itinerary(
           tuple(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:132 Mutant #52`

  ```diff
  @@ -129,7 +129,7 @@
           raise ValueError('The selected itinerary does not belong to this cargo.')
       legs = payload.get('legs')
       if not isinstance(legs, list) or not legs:
  -        raise ValueError('The selected itinerary has no legs.')
  +        raise ValueError('XXThe selected itinerary has no legs.XX')
       return Itinerary(
           tuple(
               Leg(
  ```

