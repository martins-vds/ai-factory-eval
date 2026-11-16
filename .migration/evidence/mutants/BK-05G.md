# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.935, threshold 0.8, killed 43, survived 3. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:40 Mutant #15`

  ```diff
  @@ -37,7 +37,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:43 Mutant #19`

  ```diff
  @@ -40,7 +40,7 @@
           destination_error = ''
           if request.method == 'POST':
  -            destination_code = request.POST.get('destination', '')
  +            destination_code = request.POST.get('destination', 'XXXX')
               destination = next(
                   (
                       location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:78 Mutant #33`

  ```diff
  @@ -75,7 +75,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

