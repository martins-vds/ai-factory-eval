# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.938, threshold 0.8, killed 75, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:74 Mutant #36`

  ```diff
  @@ -71,7 +71,7 @@
           destinations = [
               location for location in locations if location not in {origin, current_destination}
           ]
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:76 Mutant #40`

  ```diff
  @@ -73,7 +73,7 @@
           ]
           destination_error = ''
           if request.method == 'POST':
  -            destination_code = request.POST.get('destination', '')
  +            destination_code = request.POST.get('destination', 'XXXX')
               destination = next(
                   (
                       location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:86 Mutant #45`

  ```diff
  @@ -83,7 +83,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = 'XXSelect a valid destination.XX'
               else:
                   cargo_specification.change_destination(cargo.tracking_id, destination)
                   return _complete_dialog(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:112 Mutant #66`

  ```diff
  @@ -109,7 +109,7 @@
           deadline = cargo.route_specification.arrival_deadline
           deadline_value = f'{deadline.month}/{deadline.day}/{deadline.year % 100:02d}'
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:118 Mutant #73`

  ```diff
  @@ -115,7 +115,7 @@
               try:
                   parsed_deadline = _parse_deadline(deadline_value)
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   cargo_specification.change_deadline(cargo.tracking_id, parsed_deadline)
                   return _complete_dialog(request)
  ```

