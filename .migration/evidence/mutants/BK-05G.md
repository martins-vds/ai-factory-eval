# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `715133b6d39c3c7e9d5a0ead603b7c04446096df`): score 0.902, threshold 0.8, killed 46, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

