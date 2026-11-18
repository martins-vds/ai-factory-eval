# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `origin/main`): score 0.718, threshold 0.8, killed 61, survived 24. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:19 Mutant #1`

  ```diff
  @@ -16,7 +16,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'booking.route-selection'
  +_CANDIDATE_SALT = 'XXbooking.route-selectionXX'
   _CANDIDATE_MAX_AGE = 15 * 60
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:19 Mutant #2`

  ```diff
  @@ -16,7 +16,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'booking.route-selection'
  +_CANDIDATE_SALT = None
   _CANDIDATE_MAX_AGE = 15 * 60
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:20 Mutant #3`

  ```diff
  @@ -17,7 +17,7 @@
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
   _CANDIDATE_SALT = 'booking.route-selection'
  -_CANDIDATE_MAX_AGE = 15 * 60
  +_CANDIDATE_MAX_AGE = 16 * 60
   def _candidate_token(tracking_id: str, itinerary: Itinerary) -> str:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:20 Mutant #4`

  ```diff
  @@ -17,7 +17,7 @@
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
   _CANDIDATE_SALT = 'booking.route-selection'
  -_CANDIDATE_MAX_AGE = 15 * 60
  +_CANDIDATE_MAX_AGE = 15 / 60
   def _candidate_token(tracking_id: str, itinerary: Itinerary) -> str:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:20 Mutant #5`

  ```diff
  @@ -17,7 +17,7 @@
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
   _CANDIDATE_SALT = 'booking.route-selection'
  -_CANDIDATE_MAX_AGE = 15 * 60
  +_CANDIDATE_MAX_AGE = 15 * 61
   def _candidate_token(tracking_id: str, itinerary: Itinerary) -> str:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:20 Mutant #6`

  ```diff
  @@ -17,7 +17,7 @@
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
   _CANDIDATE_SALT = 'booking.route-selection'
  -_CANDIDATE_MAX_AGE = 15 * 60
  +_CANDIDATE_MAX_AGE = None
   def _candidate_token(tracking_id: str, itinerary: Itinerary) -> str:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:50 Mutant #22`

  ```diff
  @@ -47,7 +47,7 @@
   def _itinerary_from_token(token: str, tracking_id: str) -> Itinerary:
       payload = signing.loads(token, salt=_CANDIDATE_SALT, max_age=_CANDIDATE_MAX_AGE)
  -    if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id:
  +    if not isinstance(payload, dict) and payload.get('tracking_id') != tracking_id:
           raise signing.BadSignature
       legs = payload.get('legs')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:54 Mutant #27`

  ```diff
  @@ -51,7 +51,7 @@
           raise signing.BadSignature
       legs = payload.get('legs')
  -    if not isinstance(legs, list) or not legs:
  +    if not isinstance(legs, list) and not legs:
           raise signing.BadSignature
       return Itinerary(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:74 Mutant #42`

  ```diff
  @@ -71,7 +71,7 @@
   ) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
       def page(request: HttpRequest, tracking_id: str, select_itinerary: bool) -> HttpResponse:
           if request.method not in {'GET', 'POST'}:
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['XXGETXX', 'POST'])
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:74 Mutant #43`

  ```diff
  @@ -71,7 +71,7 @@
   ) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
       def page(request: HttpRequest, tracking_id: str, select_itinerary: bool) -> HttpResponse:
           if request.method not in {'GET', 'POST'}:
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['GET', 'XXPOSTXX'])
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:78 Mutant #46`

  ```diff
  @@ -75,7 +75,7 @@
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           candidate_error = ''
           response_status = 200
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:80 Mutant #47`

  ```diff
  @@ -77,7 +77,7 @@
           if cargo is None:
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  -        candidate_error = ''
  +        candidate_error = 'XXXX'
           response_status = 200
           if request.method == 'POST':
               try:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:80 Mutant #48`

  ```diff
  @@ -77,7 +77,7 @@
           if cargo is None:
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  -        candidate_error = ''
  +        candidate_error = None
           response_status = 200
           if request.method == 'POST':
               try:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:81 Mutant #50`

  ```diff
  @@ -78,7 +78,7 @@
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
           candidate_error = ''
  -        response_status = 200
  +        response_status = None
           if request.method == 'POST':
               try:
                   itinerary = _itinerary_from_token(request.POST.get('candidate', ''), tracking_id)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:84 Mutant #54`

  ```diff
  @@ -81,7 +81,7 @@
           response_status = 200
           if request.method == 'POST':
               try:
  -                itinerary = _itinerary_from_token(request.POST.get('candidate', ''), tracking_id)
  +                itinerary = _itinerary_from_token(request.POST.get('candidate', 'XXXX'), tracking_id)
               except (signing.BadSignature, KeyError, TypeError, ValueError):
                   candidate_error = 'Choose a valid route.'
                   response_status = 400
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:86 Mutant #56`

  ```diff
  @@ -83,7 +83,7 @@
               try:
                   itinerary = _itinerary_from_token(request.POST.get('candidate', ''), tracking_id)
               except (signing.BadSignature, KeyError, TypeError, ValueError):
  -                candidate_error = 'Choose a valid route.'
  +                candidate_error = 'XXChoose a valid route.XX'
                   response_status = 400
               else:
                   if not cargo.route_specification.is_satisfied_by(itinerary):
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:91 Mutant #61`

  ```diff
  @@ -88,7 +88,7 @@
               else:
                   if not cargo.route_specification.is_satisfied_by(itinerary):
                       candidate_error = (
  -                        'Choose a route that satisfies the current route specification.'
  +                        'XXChoose a route that satisfies the current route specification.XX'
                       )
                       response_status = 400
                   else:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:92 Mutant #62`

  ```diff
  @@ -87,9 +87,7 @@
                   response_status = 400
               else:
                   if not cargo.route_specification.is_satisfied_by(itinerary):
  -                    candidate_error = (
  -                        'Choose a route that satisfies the current route specification.'
  -                    )
  +                    candidate_error = None
                       response_status = 400
                   else:
                       routing.assign_route(TrackingId(tracking_id), itinerary)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:93 Mutant #63`

  ```diff
  @@ -90,7 +90,7 @@
                       candidate_error = (
                           'Choose a route that satisfies the current route specification.'
                       )
  -                    response_status = 400
  +                    response_status = 401
                   else:
                       routing.assign_route(TrackingId(tracking_id), itinerary)
                       return redirect(f'/admin/cargo/{tracking_id}/')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:93 Mutant #64`

  ```diff
  @@ -90,7 +90,7 @@
                       candidate_error = (
                           'Choose a route that satisfies the current route specification.'
                       )
  -                    response_status = 400
  +                    response_status = None
                   else:
                       routing.assign_route(TrackingId(tracking_id), itinerary)
                       return redirect(f'/admin/cargo/{tracking_id}/')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:107 Mutant #71`

  ```diff
  @@ -104,7 +104,7 @@
               for number, itinerary in enumerate(routing.route_candidates(TrackingId(tracking_id)), 1)
           ]
           empty_message = (
  -            'No routes found that satisfy the route specification. '
  +            'XXNo routes found that satisfy the route specification. XX'
               'Try setting an arrival deadline further into the future (a few weeks at least).'
               if select_itinerary
               else 'No routes found that satisfy the route specification. '
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:108 Mutant #72`

  ```diff
  @@ -105,7 +105,7 @@
           ]
           empty_message = (
               'No routes found that satisfy the route specification. '
  -            'Try setting an arrival deadline further into the future (a few weeks at least).'
  +            'XXTry setting an arrival deadline further into the future (a few weeks at least).XX'
               if select_itinerary
               else 'No routes found that satisfy the route specification. '
               'Try setting an arrival deadline further into the future.'
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:110 Mutant #73`

  ```diff
  @@ -107,7 +107,7 @@
               'No routes found that satisfy the route specification. '
               'Try setting an arrival deadline further into the future (a few weeks at least).'
               if select_itinerary
  -            else 'No routes found that satisfy the route specification. '
  +            else 'XXNo routes found that satisfy the route specification. XX'
               'Try setting an arrival deadline further into the future.'
           )
           return render(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:111 Mutant #74`

  ```diff
  @@ -108,7 +108,7 @@
               'Try setting an arrival deadline further into the future (a few weeks at least).'
               if select_itinerary
               else 'No routes found that satisfy the route specification. '
  -            'Try setting an arrival deadline further into the future.'
  +            'XXTry setting an arrival deadline further into the future.XX'
           )
           return render(
               request,
  ```

