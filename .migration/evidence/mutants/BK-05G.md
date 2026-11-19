# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.952, threshold 0.8, killed 59, survived 3. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:23 Mutant #3`

  ```diff
  @@ -20,7 +20,7 @@
       def find_cargo(tracking_id: str) -> Cargo:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           return cargo
       def refreshed_table(request: HttpRequest) -> HttpResponse:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:62 Mutant #38`

  ```diff
  @@ -59,7 +59,7 @@
                   None,
               )
               if destination is None:
  -                context['destination_error'] = 'Select a valid destination.'
  +                context['destination_error'] = 'XXSelect a valid destination.XX'
               else:
                   try:
                       cargo_specification.change_destination(cargo.tracking_id, destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:89 Mutant #58`

  ```diff
  @@ -86,7 +86,7 @@
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  -                context['deadline_error'] = 'Enter a valid arrival deadline.'
  +                context['deadline_error'] = 'XXEnter a valid arrival deadline.XX'
               else:
                   try:
                       cargo_specification.change_deadline(
  ```

