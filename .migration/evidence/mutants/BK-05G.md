# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.948, threshold 0.8, killed 55, survived 3. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:54 Mutant #24`

  ```diff
  @@ -51,7 +51,7 @@
               if location != cargo.route_specification.origin
               and location != cargo.route_specification.destination
           ]
  -        error = ''
  +        error = None
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:57 Mutant #28`

  ```diff
  @@ -54,7 +54,7 @@
           error = ''
           if request.method == 'POST':
  -            destination_code = request.POST.get('destination', '')
  +            destination_code = request.POST.get('destination', 'XXXX')
               destination = next(
                   (
                       location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:95 Mutant #46`

  ```diff
  @@ -92,7 +92,7 @@
           if cargo is None:
               return _not_found_response(request, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

