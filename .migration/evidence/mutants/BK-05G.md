# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.760, threshold 0.8, killed 38, survived 12. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:24 Mutant #8`

  ```diff
  @@ -21,7 +21,7 @@
   def _cargo_context(cargo_dashboard: CargoDashboard, tracking_id: str):
       cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       return cargo
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:33 Mutant #11`

  ```diff
  @@ -30,7 +30,7 @@
       cargo_dashboard: CargoDashboard,
       list_shipping_locations: Callable[[], list[Location]],
   ) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
  -    @require_http_methods(['GET', 'POST'])
  +
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _cargo_context(cargo_dashboard, tracking_id)
           locations = list_shipping_locations()
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:46 Mutant #16`

  ```diff
  @@ -43,7 +43,7 @@
                   cargo.route_specification.destination,
               )
           ]
  -        error = ''
  +        error = 'XXXX'
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:46 Mutant #17`

  ```diff
  @@ -43,7 +43,7 @@
                   cargo.route_specification.destination,
               )
           ]
  -        error = ''
  +        error = None
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:49 Mutant #21`

  ```diff
  @@ -46,7 +46,7 @@
           error = ''
           if request.method == 'POST':
  -            destination_code = request.POST.get('destination', '')
  +            destination_code = request.POST.get('destination', 'XXXX')
               destination = next(
                   (
                       location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:59 Mutant #26`

  ```diff
  @@ -56,7 +56,7 @@
                   None,
               )
               if destination is None:
  -                error = 'Select a valid destination.'
  +                error = 'XXSelect a valid destination.XX'
               else:
                   cargo_specification.change_destination(cargo.tracking_id, destination)
                   return _dialog_completion()
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:69 Mutant #30`

  ```diff
  @@ -66,7 +66,7 @@
               'booking/dialogs/destination_form.html',
               {
                   'cargo': cargo,
  -                'destinations': destinations,
  +                'XXdestinationsXX': destinations,
                   'error': error,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:74 Mutant #34`

  ```diff
  @@ -71,7 +71,6 @@
               },
           )
  -    @require_http_methods(['GET', 'POST'])
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _cargo_context(cargo_dashboard, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:78 Mutant #37`

  ```diff
  @@ -75,7 +75,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _cargo_context(cargo_dashboard, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = 'XXXX'
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:78 Mutant #38`

  ```diff
  @@ -75,7 +75,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _cargo_context(cargo_dashboard, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:81 Mutant #42`

  ```diff
  @@ -78,7 +78,7 @@
           error = ''
           if request.method == 'POST':
  -            deadline_value = request.POST.get('deadline', '')
  +            deadline_value = request.POST.get('deadline', 'XXXX')
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:85 Mutant #45`

  ```diff
  @@ -82,7 +82,7 @@
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  -                error = 'Enter a valid arrival deadline.'
  +                error = 'XXEnter a valid arrival deadline.XX'
               else:
                   cargo_specification.change_deadline(
                       cargo.tracking_id,
  ```

