# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `origin/main`): score 0.655, threshold 0.8, killed 19, survived 10. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:16 Mutant #3`

  ```diff
  @@ -13,7 +13,7 @@
       cargo_dashboard: CargoDashboard,
       cargo_routing: CargoRouting,
   ) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
  -    @require_http_methods(['GET', 'POST'])
  +
       def select_route(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo_tracking_id = TrackingId(tracking_id)
           cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:21 Mutant #7`

  ```diff
  @@ -18,7 +18,7 @@
           cargo_tracking_id = TrackingId(tracking_id)
           cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           candidates = cargo_routing.route_candidates(cargo_tracking_id)
           selection_error = None
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:24 Mutant #9`

  ```diff
  @@ -21,7 +21,7 @@
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
           candidates = cargo_routing.route_candidates(cargo_tracking_id)
  -        selection_error = None
  +        selection_error = ""
           if request.method == 'POST':
               try:
                   candidate_index = int(request.POST.get('candidate_index', ''))
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:27 Mutant #13`

  ```diff
  @@ -24,7 +24,7 @@
           selection_error = None
           if request.method == 'POST':
               try:
  -                candidate_index = int(request.POST.get('candidate_index', ''))
  +                candidate_index = int(request.POST.get('candidate_index', 'XXXX'))
               except ValueError:
                   candidate_index = -1
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:29 Mutant #15`

  ```diff
  @@ -26,7 +26,7 @@
               try:
                   candidate_index = int(request.POST.get('candidate_index', ''))
               except ValueError:
  -                candidate_index = -1
  +                candidate_index = +1
               if not 0 <= candidate_index < len(candidates):
                   selection_error = 'Select a valid itinerary.'
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:29 Mutant #16`

  ```diff
  @@ -26,7 +26,7 @@
               try:
                   candidate_index = int(request.POST.get('candidate_index', ''))
               except ValueError:
  -                candidate_index = -1
  +                candidate_index = -2
               if not 0 <= candidate_index < len(candidates):
                   selection_error = 'Select a valid itinerary.'
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:29 Mutant #17`

  ```diff
  @@ -26,7 +26,7 @@
               try:
                   candidate_index = int(request.POST.get('candidate_index', ''))
               except ValueError:
  -                candidate_index = -1
  +                candidate_index = None
               if not 0 <= candidate_index < len(candidates):
                   selection_error = 'Select a valid itinerary.'
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:31 Mutant #19`

  ```diff
  @@ -28,7 +28,7 @@
               except ValueError:
                   candidate_index = -1
  -            if not 0 <= candidate_index < len(candidates):
  +            if not 1 <= candidate_index < len(candidates):
                   selection_error = 'Select a valid itinerary.'
               else:
                   cargo_routing.assign_route(cargo_tracking_id, candidates[candidate_index])
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:31 Mutant #20`

  ```diff
  @@ -28,7 +28,7 @@
               except ValueError:
                   candidate_index = -1
  -            if not 0 <= candidate_index < len(candidates):
  +            if not 0 < candidate_index < len(candidates):
                   selection_error = 'Select a valid itinerary.'
               else:
                   cargo_routing.assign_route(cargo_tracking_id, candidates[candidate_index])
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:32 Mutant #22`

  ```diff
  @@ -29,7 +29,7 @@
                   candidate_index = -1
               if not 0 <= candidate_index < len(candidates):
  -                selection_error = 'Select a valid itinerary.'
  +                selection_error = 'XXSelect a valid itinerary.XX'
               else:
                   cargo_routing.assign_route(cargo_tracking_id, candidates[candidate_index])
                   return redirect(f'/admin/cargo/{cargo_tracking_id.value}/')
  ```

