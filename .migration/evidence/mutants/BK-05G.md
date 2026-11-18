# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.962, threshold 0.8, killed 50, survived 2. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:51 Mutant #21`

  ```diff
  @@ -48,7 +48,7 @@
                   cargo.route_specification.destination,
               )
           ]
  -        destination_error = None
  +        destination_error = ""
           if request.method == 'POST':
               destination_value = request.POST.get('destination')
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:91 Mutant #39`

  ```diff
  @@ -88,7 +88,7 @@
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           submitted_deadline = request.POST.get('deadline')
  -        deadline_error = None
  +        deadline_error = ""
           if request.method == 'POST':
               try:
                   if submitted_deadline is None:
  ```

