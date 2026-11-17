# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.923, threshold 0.8, killed 60, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:16 Mutant #1`

  ```diff
  @@ -13,7 +13,7 @@
   def _dialog_template(request: HttpRequest, fragment: str, page: str) -> str:
  -    return fragment if request.headers.get('HX-Request') == 'true' else page
  +    return fragment if request.headers.get('XXHX-RequestXX') == 'true' else page
   def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:16 Mutant #3`

  ```diff
  @@ -13,7 +13,7 @@
   def _dialog_template(request: HttpRequest, fragment: str, page: str) -> str:
  -    return fragment if request.headers.get('HX-Request') == 'true' else page
  +    return fragment if request.headers.get('HX-Request') == 'XXtrueXX' else page
   def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:22 Mutant #6`

  ```diff
  @@ -19,7 +19,7 @@
   def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
       cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       return cargo
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:72 Mutant #40`

  ```diff
  @@ -69,7 +69,7 @@
                   None,
               )
               if destination is None:
  -                context['destination_error'] = 'Select a valid destination.'
  +                context['destination_error'] = 'XXSelect a valid destination.XX'
               else:
                   cargo_specification.change_destination(TrackingId(tracking_id), destination)
                   return _complete_dialog_update(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:106 Mutant #62`

  ```diff
  @@ -103,7 +103,7 @@
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  -                context['deadline_error'] = 'Enter a valid arrival deadline.'
  +                context['deadline_error'] = 'XXEnter a valid arrival deadline.XX'
               else:
                   cargo_specification.change_deadline(
                       TrackingId(tracking_id),
  ```

