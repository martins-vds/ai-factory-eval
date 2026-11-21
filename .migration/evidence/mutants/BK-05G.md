# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `256fbe36bcab1dc38117715631d54b7d8cefc2c0`): score 0.904, threshold 0.8, killed 47, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:81 Mutant #31`

  ```diff
  @@ -78,7 +78,7 @@
                   return render(
                       request,
                       'booking/dialogs/destination.html',
  -                    _destination_context(cargo, locations, 'Select a valid destination.'),
  +                    _destination_context(cargo, locations, 'XXSelect a valid destination.XX'),
                   )
               cargo_specification.change_destination(cargo.tracking_id, destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:105 Mutant #42`

  ```diff
  @@ -102,7 +102,7 @@
           deadline = cargo.route_specification.arrival_deadline.date()
           if request.method == 'POST':
  -            deadline_value = request.POST.get('deadline', '')
  +            deadline_value = request.POST.get('deadline', 'XXXX')
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:113 Mutant #46`

  ```diff
  @@ -110,7 +110,7 @@
                       request,
                       'booking/dialogs/deadline.html',
                       {
  -                        'cargo': cargo,
  +                        'XXcargoXX': cargo,
                           'deadline': deadline_value,
                           'deadline_error': 'Enter a valid arrival deadline.',
                       },
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:114 Mutant #47`

  ```diff
  @@ -111,7 +111,7 @@
                       'booking/dialogs/deadline.html',
                       {
                           'cargo': cargo,
  -                        'deadline': deadline_value,
  +                        'XXdeadlineXX': deadline_value,
                           'deadline_error': 'Enter a valid arrival deadline.',
                       },
                   )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:115 Mutant #49`

  ```diff
  @@ -112,7 +112,7 @@
                       {
                           'cargo': cargo,
                           'deadline': deadline_value,
  -                        'deadline_error': 'Enter a valid arrival deadline.',
  +                        'deadline_error': 'XXEnter a valid arrival deadline.XX',
                       },
                   )
  ```

