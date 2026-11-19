# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.787, threshold 0.8, killed 37, survived 10. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

- `src/cargotracker/booking/interfaces/dialogs/views.py:45 Mutant #24`

  ```diff
  @@ -42,7 +42,7 @@
                   None,
               )
               if destination is None:
  -                error = 'Select a valid destination.'
  +                error = 'XXSelect a valid destination.XX'
               else:
                   cargo_specification.change_destination(TrackingId(tracking_id), destination)
                   return _dialog_completion(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:45 Mutant #25`

  ```diff
  @@ -42,7 +42,7 @@
                   None,
               )
               if destination is None:
  -                error = 'Select a valid destination.'
  +                error = None
               else:
                   cargo_specification.change_destination(TrackingId(tracking_id), destination)
                   return _dialog_completion(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:53 Mutant #29`

  ```diff
  @@ -50,7 +50,7 @@
           return render(
               request,
               'booking/dialogs/destination.html',
  -            {'cargo': cargo, 'locations': locations, 'error': error},
  +            {'cargo': cargo, 'locations': locations, 'XXerrorXX': error},
           )
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
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

- `src/cargotracker/booking/interfaces/dialogs/views.py:64 Mutant #39`

  ```diff
  @@ -61,7 +61,7 @@
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           error = ''
           if request.method == 'POST':
  -            deadline_value = request.POST.get('deadline', '')
  +            deadline_value = request.POST.get('deadline', 'XXXX')
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:68 Mutant #42`

  ```diff
  @@ -65,7 +65,7 @@
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  -                error = 'Enter a valid arrival deadline.'
  +                error = 'XXEnter a valid arrival deadline.XX'
               else:
                   cargo_specification.change_deadline(
                       TrackingId(tracking_id),
  ```

