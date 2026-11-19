# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.894, threshold 0.8, killed 42, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:29 Mutant #11`

  ```diff
  @@ -26,7 +26,7 @@
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           locations = [
               location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:37 Mutant #15`

  ```diff
  @@ -34,7 +34,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        error = ''
  +        error = None
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:39 Mutant #19`

  ```diff
  @@ -36,7 +36,7 @@
           ]
           error = ''
           if request.method == 'POST':
  -            destination_code = request.POST.get('destination', '')
  +            destination_code = request.POST.get('destination', 'XXXX')
               destination = next(
                   (location for location in locations if location.unlocode.value == destination_code),
                   None,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:59 Mutant #32`

  ```diff
  @@ -56,7 +56,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           error = ''
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:62 Mutant #35`

  ```diff
  @@ -59,7 +59,7 @@
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

