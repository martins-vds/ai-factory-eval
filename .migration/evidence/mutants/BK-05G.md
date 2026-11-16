# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.923, threshold 0.8, killed 48, survived 4. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:27 Mutant #7`

  ```diff
  @@ -24,7 +24,7 @@
           cargo_tracking_id = TrackingId(tracking_id)
           cargo = cargo_repository.find(cargo_tracking_id)
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           destinations = [
               location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:35 Mutant #11`

  ```diff
  @@ -32,7 +32,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        error = ''
  +        error = None
           if request.method == 'POST':
               destination = next(
                   (
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:70 Mutant #31`

  ```diff
  @@ -67,7 +67,7 @@
           cargo_tracking_id = TrackingId(tracking_id)
           cargo = cargo_repository.find(cargo_tracking_id)
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           error = ''
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:73 Mutant #34`

  ```diff
  @@ -70,7 +70,7 @@
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('arrival_deadline', '')
               try:
  ```

