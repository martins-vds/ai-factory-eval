# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `cce147dc5b1f06341760dbe4bbf1925210133037`): score 0.838, threshold 0.8, killed 62, survived 12. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:18 Mutant #3`

  ```diff
  @@ -15,7 +15,7 @@
   def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
       cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       return cargo
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:39 Mutant #18`

  ```diff
  @@ -36,7 +36,7 @@
   def _render_dialog(
       request: HttpRequest, fragment: str, page: str, context: dict[str, object]
   ) -> HttpResponse:
  -    if request.headers.get('HX-Request') == 'true':
  +    if request.headers.get('XXHX-RequestXX') == 'true':
           return render(request, fragment, context)
       return render(request, page, {**context, 'open_dialog': True})
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:39 Mutant #20`

  ```diff
  @@ -36,7 +36,7 @@
   def _render_dialog(
       request: HttpRequest, fragment: str, page: str, context: dict[str, object]
   ) -> HttpResponse:
  -    if request.headers.get('HX-Request') == 'true':
  +    if request.headers.get('HX-Request') == 'XXtrueXX':
           return render(request, fragment, context)
       return render(request, page, {**context, 'open_dialog': True})
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:41 Mutant #22`

  ```diff
  @@ -38,7 +38,7 @@
   ) -> HttpResponse:
       if request.headers.get('HX-Request') == 'true':
           return render(request, fragment, context)
  -    return render(request, page, {**context, 'open_dialog': True})
  +    return render(request, page, {**context, 'XXopen_dialogXX': True})
   def _destination_options(cargo: Cargo, locations: list[Location]) -> list[Location]:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:41 Mutant #23`

  ```diff
  @@ -38,7 +38,7 @@
   ) -> HttpResponse:
       if request.headers.get('HX-Request') == 'true':
           return render(request, fragment, context)
  -    return render(request, page, {**context, 'open_dialog': True})
  +    return render(request, page, {**context, 'open_dialog': False})
   def _destination_options(cargo: Cargo, locations: list[Location]) -> list[Location]:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:56 Mutant #25`

  ```diff
  @@ -53,7 +53,7 @@
       cargo: Cargo,
       tracking_id: str,
       destinations: list[Location],
  -    destination_value: str = '',
  +    destination_value: str = 'XXXX',
       destination_error: str = '',
   ) -> dict[str, object]:
       if not destination_value and destinations:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:57 Mutant #26`

  ```diff
  @@ -54,7 +54,7 @@
       tracking_id: str,
       destinations: list[Location],
       destination_value: str = '',
  -    destination_error: str = '',
  +    destination_error: str = 'XXXX',
   ) -> dict[str, object]:
       if not destination_value and destinations:
           destination_value = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:59 Mutant #28`

  ```diff
  @@ -56,7 +56,7 @@
       destination_value: str = '',
       destination_error: str = '',
   ) -> dict[str, object]:
  -    if not destination_value and destinations:
  +    if not destination_value or destinations:
           destination_value = next(
               (
                   location.unlocode.value
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:87 Mutant #46`

  ```diff
  @@ -84,7 +84,7 @@
           locations = list(list_shipping_locations())
           destinations = _destination_options(cargo, locations)
           destination_value = request.POST.get('destination', '')
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:99 Mutant #52`

  ```diff
  @@ -96,7 +96,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = 'XXSelect a valid destination.XX'
               else:
                   cargo_specification.change_destination(TrackingId(tracking_id), destination)
                   return _updated_table(request, cargo_dashboard)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:123 Mutant #61`

  ```diff
  @@ -120,7 +120,7 @@
           deadline_value = request.POST.get(
               'deadline', cargo.route_specification.arrival_deadline.date().isoformat()
           )
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:129 Mutant #65`

  ```diff
  @@ -126,7 +126,7 @@
               try:
                   arrival_date = date.fromisoformat(deadline_value)
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   arrival_deadline = timezone.make_aware(
                       datetime.combine(arrival_date, time.min),
  ```

