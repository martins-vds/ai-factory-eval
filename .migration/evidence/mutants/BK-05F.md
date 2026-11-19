# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `origin/main`): score 0.794, threshold 0.8, killed 50, survived 13. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:28 Mutant #1`

  ```diff
  @@ -25,7 +25,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'booking.route-selection.candidate'
  +_CANDIDATE_SALT = 'XXbooking.route-selection.candidateXX'
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:28 Mutant #2`

  ```diff
  @@ -25,7 +25,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'booking.route-selection.candidate'
  +_CANDIDATE_SALT = None
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:36 Mutant #5`

  ```diff
  @@ -33,7 +33,7 @@
       cargo_routing: CargoRouting,
   ) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
       def route(request: HttpRequest, tracking_id: str) -> HttpResponse:
  -        if request.method not in {'GET', 'HEAD'}:
  +        if request.method not in {'GET', 'XXHEADXX'}:
               return HttpResponseNotAllowed(('GET', 'HEAD'))
           return _render_candidates(request, tracking_id, select_itinerary=False)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:37 Mutant #6`

  ```diff
  @@ -34,7 +34,7 @@
   ) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
       def route(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'HEAD'}:
  -            return HttpResponseNotAllowed(('GET', 'HEAD'))
  +            return HttpResponseNotAllowed(('XXGETXX', 'HEAD'))
           return _render_candidates(request, tracking_id, select_itinerary=False)
       def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:37 Mutant #7`

  ```diff
  @@ -34,7 +34,7 @@
   ) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
       def route(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'HEAD'}:
  -            return HttpResponseNotAllowed(('GET', 'HEAD'))
  +            return HttpResponseNotAllowed(('GET', 'XXHEADXX'))
           return _render_candidates(request, tracking_id, select_itinerary=False)
       def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:41 Mutant #9`

  ```diff
  @@ -38,7 +38,7 @@
           return _render_candidates(request, tracking_id, select_itinerary=False)
       def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
  -        cargo = _get_cargo(tracking_id)
  +        cargo = None
           if request.method == 'POST':
               itinerary = _submitted_itinerary(request, tracking_id)
               if itinerary is None:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:47 Mutant #15`

  ```diff
  @@ -44,7 +44,7 @@
               if itinerary is None:
                   return HttpResponseBadRequest('Invalid route selection.')
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
  -            cargo_details_path = quote(tracking_id, safe='')
  +            cargo_details_path = quote(tracking_id, safe='XXXX')
               cargo_details_url = f'/admin/cargo/{cargo_details_path}/'
               if not url_has_allowed_host_and_scheme(
                   cargo_details_url,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:54 Mutant #20`

  ```diff
  @@ -51,7 +51,7 @@
                   allowed_hosts={request.get_host()},
                   require_https=request.is_secure(),
               ):
  -                return HttpResponseBadRequest('Invalid cargo details redirect.')
  +                return HttpResponseBadRequest('XXInvalid cargo details redirect.XX')
               return redirect(cargo_details_url)
           if request.method not in {'GET', 'HEAD'}:
               return HttpResponseNotAllowed(('GET', 'HEAD', 'POST'))
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:56 Mutant #23`

  ```diff
  @@ -53,7 +53,7 @@
               ):
                   return HttpResponseBadRequest('Invalid cargo details redirect.')
               return redirect(cargo_details_url)
  -        if request.method not in {'GET', 'HEAD'}:
  +        if request.method not in {'GET', 'XXHEADXX'}:
               return HttpResponseNotAllowed(('GET', 'HEAD', 'POST'))
           return _render_candidates(
               request,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:57 Mutant #24`

  ```diff
  @@ -54,7 +54,7 @@
                   return HttpResponseBadRequest('Invalid cargo details redirect.')
               return redirect(cargo_details_url)
           if request.method not in {'GET', 'HEAD'}:
  -            return HttpResponseNotAllowed(('GET', 'HEAD', 'POST'))
  +            return HttpResponseNotAllowed(('XXGETXX', 'HEAD', 'POST'))
           return _render_candidates(
               request,
               tracking_id,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:57 Mutant #25`

  ```diff
  @@ -54,7 +54,7 @@
                   return HttpResponseBadRequest('Invalid cargo details redirect.')
               return redirect(cargo_details_url)
           if request.method not in {'GET', 'HEAD'}:
  -            return HttpResponseNotAllowed(('GET', 'HEAD', 'POST'))
  +            return HttpResponseNotAllowed(('GET', 'XXHEADXX', 'POST'))
           return _render_candidates(
               request,
               tracking_id,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:57 Mutant #26`

  ```diff
  @@ -54,7 +54,7 @@
                   return HttpResponseBadRequest('Invalid cargo details redirect.')
               return redirect(cargo_details_url)
           if request.method not in {'GET', 'HEAD'}:
  -            return HttpResponseNotAllowed(('GET', 'HEAD', 'POST'))
  +            return HttpResponseNotAllowed(('GET', 'HEAD', 'XXPOSTXX'))
           return _render_candidates(
               request,
               tracking_id,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:68 Mutant #30`

  ```diff
  @@ -65,7 +65,7 @@
       def _get_cargo(tracking_id: str):
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           return cargo
       def _render_candidates(
  ```

