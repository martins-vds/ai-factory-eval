# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.970, threshold 0.8, killed 64, survived 2. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:49 Mutant #23`

  ```diff
  @@ -46,7 +46,7 @@
               for location in locations
               if location not in (route_specification.origin, route_specification.destination)
           ]
  -        error = ''
  +        error = None
           if request.method == 'POST':
               destination_code = request.POST.get('destination')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:85 Mutant #50`

  ```diff
  @@ -82,7 +82,7 @@
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           route_specification = cargo.route_specification
           deadline_value = route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

