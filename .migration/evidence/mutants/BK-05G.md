# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.892, threshold 0.8, killed 58, survived 7. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:53 Mutant #24`

  ```diff
  @@ -50,7 +50,7 @@
                   cargo.route_specification.destination,
               )
           ]
  -        selected_destination = request.POST.get('destination', '')
  +        selected_destination = request.POST.get('destination', 'XXXX')
           if request.method == 'POST':
               destination_by_code = {location.unlocode.value: location for location in locations}
               destination = destination_by_code.get(selected_destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:64 Mutant #34`

  ```diff
  @@ -61,7 +61,7 @@
                       {
                           'cargo': cargo,
                           'locations': locations,
  -                        'selected_destination': selected_destination,
  +                        'XXselected_destinationXX': selected_destination,
                           'destination_error': 'Select an available destination.',
                       },
                   )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:65 Mutant #36`

  ```diff
  @@ -62,7 +62,7 @@
                           'cargo': cargo,
                           'locations': locations,
                           'selected_destination': selected_destination,
  -                        'destination_error': 'Select an available destination.',
  +                        'destination_error': 'XXSelect an available destination.XX',
                       },
                   )
               specification.change_destination(cargo.tracking_id, destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:77 Mutant #40`

  ```diff
  @@ -74,7 +74,7 @@
               {
                   'cargo': cargo,
                   'locations': locations,
  -                'selected_destination': selected_destination,
  +                'XXselected_destinationXX': selected_destination,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:100 Mutant #54`

  ```diff
  @@ -97,7 +97,7 @@
               if request.method == 'POST'
               else timezone.localtime(cargo.route_specification.arrival_deadline).strftime('%Y-%m-%d')
           )
  -        deadline_error = ''
  +        deadline_error = 'XXXX'
           if request.method == 'POST':
               try:
                   arrival_deadline = datetime.strptime(deadline_value, '%Y-%m-%d').date()
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:100 Mutant #55`

  ```diff
  @@ -97,7 +97,7 @@
               if request.method == 'POST'
               else timezone.localtime(cargo.route_specification.arrival_deadline).strftime('%Y-%m-%d')
           )
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               try:
                   arrival_deadline = datetime.strptime(deadline_value, '%Y-%m-%d').date()
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:105 Mutant #60`

  ```diff
  @@ -102,7 +102,7 @@
               try:
                   arrival_deadline = datetime.strptime(deadline_value, '%Y-%m-%d').date()
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   specification.change_deadline(
                       cargo.tracking_id,
  ```

