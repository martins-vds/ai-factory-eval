# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.917, threshold 0.8, killed 55, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:18 Mutant #3`

  ```diff
  @@ -15,7 +15,7 @@
   def _find_cargo(dashboard: CargoDashboard, tracking_id: str) -> Cargo:
       cargo = dashboard.get_cargo_details(TrackingId(tracking_id))
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       return cargo
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:50 Mutant #26`

  ```diff
  @@ -47,7 +47,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        error = ''
  +        error = None
           if request.method == 'POST':
               destination = next(
                   (
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:61 Mutant #33`

  ```diff
  @@ -58,7 +58,7 @@
                   None,
               )
               if destination is None:
  -                error = 'Select a valid destination.'
  +                error = 'XXSelect a valid destination.XX'
               else:
                   try:
                       cargo_specification.change_destination(TrackingId(tracking_id), destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:85 Mutant #48`

  ```diff
  @@ -82,7 +82,7 @@
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           deadline = cargo.route_specification.arrival_deadline
           deadline_value = deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:91 Mutant #55`

  ```diff
  @@ -88,7 +88,7 @@
               try:
                   selected_deadline = date.fromisoformat(deadline_value)
               except ValueError:
  -                deadline_error = 'Enter a valid date.'
  +                deadline_error = 'XXEnter a valid date.XX'
               else:
                   try:
                       cargo_specification.change_deadline(
  ```

