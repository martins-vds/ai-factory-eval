# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `715133b6d39c3c7e9d5a0ead603b7c04446096df`): score 0.784, threshold 0.8, killed 40, survived 11. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:26 Mutant #4`

  ```diff
  @@ -23,7 +23,7 @@
           cargo_tracking_id = TrackingId(tracking_id)
           cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           all_locations = list_shipping_locations()
           locations = [
               location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:34 Mutant #8`

  ```diff
  @@ -31,7 +31,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        destination_error = ''
  +        destination_error = 'XXXX'
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:34 Mutant #9`

  ```diff
  @@ -31,7 +31,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:36 Mutant #13`

  ```diff
  @@ -33,7 +33,7 @@
           ]
           destination_error = ''
           if request.method == 'POST':
  -            destination_code = request.POST.get('destination', '')
  +            destination_code = request.POST.get('destination', 'XXXX')
               destination = next(
                   (location for location in locations if location.unlocode.value == destination_code),
                   None,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:42 Mutant #18`

  ```diff
  @@ -39,7 +39,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = 'XXSelect a valid destination.XX'
               else:
                   cargo_specification.change_destination(cargo_tracking_id, destination)
                   return _dialog_completed(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:56 Mutant #27`

  ```diff
  @@ -53,7 +53,7 @@
           cargo_tracking_id = TrackingId(tracking_id)
           cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           deadline_error = ''
           if request.method == 'POST':
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:58 Mutant #29`

  ```diff
  @@ -55,7 +55,7 @@
           if cargo is None:
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = 'XXXX'
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:58 Mutant #30`

  ```diff
  @@ -55,7 +55,7 @@
           if cargo is None:
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:60 Mutant #34`

  ```diff
  @@ -57,7 +57,7 @@
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           deadline_error = ''
           if request.method == 'POST':
  -            deadline_value = request.POST.get('deadline', '')
  +            deadline_value = request.POST.get('deadline', 'XXXX')
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:64 Mutant #37`

  ```diff
  @@ -61,7 +61,7 @@
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   arrival_deadline = timezone.make_aware(datetime.combine(deadline, time.min))
                   cargo_specification.change_deadline(cargo_tracking_id, arrival_deadline)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:81 Mutant #49`

  ```diff
  @@ -78,7 +78,7 @@
   def _dialog_completed(request: HttpRequest) -> HttpResponse:
       if request.headers.get('HX-Request') == 'true':
           response = HttpResponse()
  -        response['HX-Trigger'] = 'bookingDialogCompleted'
  +        response['HX-Trigger'] = 'XXbookingDialogCompletedXX'
           return response
       return redirect('/admin/dashboard/')
  ```

