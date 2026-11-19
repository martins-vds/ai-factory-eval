# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `38ac36c4838555c7db2eb9ef3e243981b571e9f1`): score 0.837, threshold 0.8, killed 41, survived 8. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:33 Mutant #11`

  ```diff
  @@ -30,7 +30,7 @@
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           locations = list(list_shipping_locations())
           destinations = [
               location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:41 Mutant #15`

  ```diff
  @@ -38,7 +38,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        destination_error = ''
  +        destination_error = 'XXXX'
           if request.method == 'POST':
               destination_value = request.POST.get('destination', '')
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:41 Mutant #16`

  ```diff
  @@ -38,7 +38,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination_value = request.POST.get('destination', '')
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:43 Mutant #20`

  ```diff
  @@ -40,7 +40,7 @@
           ]
           destination_error = ''
           if request.method == 'POST':
  -            destination_value = request.POST.get('destination', '')
  +            destination_value = request.POST.get('destination', 'XXXX')
               destination = next(
                   (
                       location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:53 Mutant #25`

  ```diff
  @@ -50,7 +50,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = 'XXSelect a valid destination.XX'
               else:
                   cargo_specification.change_destination(TrackingId(tracking_id), destination)
                   return _dialog_completion(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:71 Mutant #33`

  ```diff
  @@ -68,7 +68,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           deadline_value = cargo.route_specification.arrival_deadline.strftime('%Y-%m-%d')
           deadline_error = ''
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:73 Mutant #37`

  ```diff
  @@ -70,7 +70,7 @@
           if cargo is None:
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
           deadline_value = cargo.route_specification.arrival_deadline.strftime('%Y-%m-%d')
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:80 Mutant #44`

  ```diff
  @@ -77,7 +77,7 @@
               try:
                   arrival_deadline = date.fromisoformat(deadline_value)
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   cargo_specification.change_deadline(
                       TrackingId(tracking_id),
  ```

