# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `origin/main`): score 0.741, threshold 0.8, killed 43, survived 15. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:26 Mutant #1`

  ```diff
  @@ -23,7 +23,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'booking.route-selection.candidate'
  +_CANDIDATE_SALT = 'XXbooking.route-selection.candidateXX'
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:26 Mutant #2`

  ```diff
  @@ -23,7 +23,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'booking.route-selection.candidate'
  +_CANDIDATE_SALT = None
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:34 Mutant #5`

  ```diff
  @@ -31,7 +31,7 @@
       cargo_routing: CargoRouting,
   ) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
       def route(request: HttpRequest, tracking_id: str) -> HttpResponse:
  -        if request.method not in {'GET', 'HEAD'}:
  +        if request.method not in {'GET', 'XXHEADXX'}:
               return HttpResponseNotAllowed(('GET', 'HEAD'))
           return _render_candidates(request, tracking_id, select_itinerary=False)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:35 Mutant #6`

  ```diff
  @@ -32,7 +32,7 @@
   ) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
       def route(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'HEAD'}:
  -            return HttpResponseNotAllowed(('GET', 'HEAD'))
  +            return HttpResponseNotAllowed(('XXGETXX', 'HEAD'))
           return _render_candidates(request, tracking_id, select_itinerary=False)
       def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:35 Mutant #7`

  ```diff
  @@ -32,7 +32,7 @@
   ) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
       def route(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'HEAD'}:
  -            return HttpResponseNotAllowed(('GET', 'HEAD'))
  +            return HttpResponseNotAllowed(('GET', 'XXHEADXX'))
           return _render_candidates(request, tracking_id, select_itinerary=False)
       def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:36 Mutant #8`

  ```diff
  @@ -33,7 +33,7 @@
       def route(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'HEAD'}:
               return HttpResponseNotAllowed(('GET', 'HEAD'))
  -        return _render_candidates(request, tracking_id, select_itinerary=False)
  +        return _render_candidates(request, tracking_id, select_itinerary=True)
       def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _get_cargo(tracking_id)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:39 Mutant #9`

  ```diff
  @@ -36,7 +36,7 @@
           return _render_candidates(request, tracking_id, select_itinerary=False)
       def select_itinerary(request: HttpRequest, tracking_id: str) -> HttpResponse:
  -        cargo = _get_cargo(tracking_id)
  +        cargo = None
           if request.method == 'POST':
               itinerary = _submitted_itinerary(request, tracking_id)
               if itinerary is None:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:43 Mutant #14`

  ```diff
  @@ -40,7 +40,7 @@
           if request.method == 'POST':
               itinerary = _submitted_itinerary(request, tracking_id)
               if itinerary is None:
  -                return HttpResponseBadRequest('Invalid route selection.')
  +                return HttpResponseBadRequest('XXInvalid route selection.XX')
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
               return redirect(f'/admin/cargo/{tracking_id}/')
           if request.method not in {'GET', 'HEAD'}:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:46 Mutant #18`

  ```diff
  @@ -43,7 +43,7 @@
                   return HttpResponseBadRequest('Invalid route selection.')
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
               return redirect(f'/admin/cargo/{tracking_id}/')
  -        if request.method not in {'GET', 'HEAD'}:
  +        if request.method not in {'GET', 'XXHEADXX'}:
               return HttpResponseNotAllowed(('GET', 'HEAD', 'POST'))
           return _render_candidates(
               request,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:47 Mutant #19`

  ```diff
  @@ -44,7 +44,7 @@
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
               return redirect(f'/admin/cargo/{tracking_id}/')
           if request.method not in {'GET', 'HEAD'}:
  -            return HttpResponseNotAllowed(('GET', 'HEAD', 'POST'))
  +            return HttpResponseNotAllowed(('XXGETXX', 'HEAD', 'POST'))
           return _render_candidates(
               request,
               tracking_id,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:47 Mutant #20`

  ```diff
  @@ -44,7 +44,7 @@
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
               return redirect(f'/admin/cargo/{tracking_id}/')
           if request.method not in {'GET', 'HEAD'}:
  -            return HttpResponseNotAllowed(('GET', 'HEAD', 'POST'))
  +            return HttpResponseNotAllowed(('GET', 'XXHEADXX', 'POST'))
           return _render_candidates(
               request,
               tracking_id,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:47 Mutant #21`

  ```diff
  @@ -44,7 +44,7 @@
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
               return redirect(f'/admin/cargo/{tracking_id}/')
           if request.method not in {'GET', 'HEAD'}:
  -            return HttpResponseNotAllowed(('GET', 'HEAD', 'POST'))
  +            return HttpResponseNotAllowed(('GET', 'HEAD', 'XXPOSTXX'))
           return _render_candidates(
               request,
               tracking_id,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:51 Mutant #22`

  ```diff
  @@ -48,7 +48,7 @@
           return _render_candidates(
               request,
               tracking_id,
  -            select_itinerary=True,
  +            select_itinerary=False,
               cargo=cargo,
           )
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:58 Mutant #25`

  ```diff
  @@ -55,7 +55,7 @@
       def _get_cargo(tracking_id: str):
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           return cargo
       def _render_candidates(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:94 Mutant #39`

  ```diff
  @@ -91,7 +91,7 @@
                   'cargo': cargo,
                   'candidates': candidates,
                   'candidate_count': len(candidates),
  -                'select_itinerary': select_itinerary,
  +                'XXselect_itineraryXX': select_itinerary,
               },
           )
  ```

