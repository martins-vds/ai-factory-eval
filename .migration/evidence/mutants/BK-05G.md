# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `cce147dc5b1f06341760dbe4bbf1925210133037`): score 0.727, threshold 0.8, killed 48, survived 18. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

- `src/cargotracker/booking/interfaces/dialogs/views.py:24 Mutant #7`

  ```diff
  @@ -21,7 +21,7 @@
   def _updated_table(request: HttpRequest, cargo_dashboard: CargoDashboard) -> HttpResponse:
       if request.headers.get('HX-Request') != 'true':
  -        return redirect('/admin/dashboard/')
  +        return redirect('XX/admin/dashboard/XX')
       cargos = cargo_dashboard.get_dashboard()
       response = render(
           request,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:40 Mutant #18`

  ```diff
  @@ -37,7 +37,7 @@
       cargo: Cargo,
       tracking_id: str,
       locations: list[Location],
  -    destination_value: str = '',
  +    destination_value: str = 'XXXX',
       destination_error: str = '',
   ) -> dict[str, object]:
       destinations = [
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:41 Mutant #19`

  ```diff
  @@ -38,7 +38,7 @@
       tracking_id: str,
       locations: list[Location],
       destination_value: str = '',
  -    destination_error: str = '',
  +    destination_error: str = 'XXXX',
   ) -> dict[str, object]:
       destinations = [
           location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:48 Mutant #23`

  ```diff
  @@ -45,7 +45,7 @@
           for location in locations
           if location not in (cargo.route_specification.origin, cargo.route_specification.destination)
       ]
  -    if not destination_value and destinations:
  +    if not destination_value or destinations:
           destination_value = next(
               (
                   location.unlocode.value
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:55 Mutant #26`

  ```diff
  @@ -52,7 +52,7 @@
                   for location in destinations
                   if location.unlocode.value == 'SEGOT'
               ),
  -            destinations[0].unlocode.value,
  +            destinations[1].unlocode.value,
           )
       return {
           'cargo': cargo,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:61 Mutant #31`

  ```diff
  @@ -58,7 +58,7 @@
           'cargo': cargo,
           'destinations': destinations,
           'destination_value': destination_value,
  -        'destination_error': destination_error,
  +        'XXdestination_errorXX': destination_error,
           'action': f'/admin/cargo/{tracking_id}/destination/',
       }
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:62 Mutant #32`

  ```diff
  @@ -59,7 +59,7 @@
           'destinations': destinations,
           'destination_value': destination_value,
           'destination_error': destination_error,
  -        'action': f'/admin/cargo/{tracking_id}/destination/',
  +        'XXactionXX': f'/admin/cargo/{tracking_id}/destination/',
       }
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:62 Mutant #33`

  ```diff
  @@ -59,7 +59,7 @@
           'destinations': destinations,
           'destination_value': destination_value,
           'destination_error': destination_error,
  -        'action': f'/admin/cargo/{tracking_id}/destination/',
  +        'action': f'XX/admin/cargo/{tracking_id}/destination/XX',
       }
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:75 Mutant #39`

  ```diff
  @@ -72,7 +72,7 @@
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           locations = list(list_shipping_locations())
           destination_value = request.POST.get('destination', '')
  -        destination_error = ''
  +        destination_error = 'XXXX'
           if request.method == 'POST':
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:75 Mutant #40`

  ```diff
  @@ -72,7 +72,7 @@
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           locations = list(list_shipping_locations())
           destination_value = request.POST.get('destination', '')
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:87 Mutant #46`

  ```diff
  @@ -84,7 +84,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = 'XXSelect a valid destination.XX'
               else:
                   cargo_specification.change_destination(TrackingId(tracking_id), destination)
                   return _updated_table(request, cargo_dashboard)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:87 Mutant #47`

  ```diff
  @@ -84,7 +84,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = None
               else:
                   cargo_specification.change_destination(TrackingId(tracking_id), destination)
                   return _updated_table(request, cargo_dashboard)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:106 Mutant #53`

  ```diff
  @@ -103,7 +103,7 @@
           deadline_value = request.POST.get(
               'deadline', cargo.route_specification.arrival_deadline.date().isoformat()
           )
  -        deadline_error = ''
  +        deadline_error = 'XXXX'
           if request.method == 'POST':
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:106 Mutant #54`

  ```diff
  @@ -103,7 +103,7 @@
           deadline_value = request.POST.get(
               'deadline', cargo.route_specification.arrival_deadline.date().isoformat()
           )
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:112 Mutant #58`

  ```diff
  @@ -109,7 +109,7 @@
               try:
                   arrival_date = date.fromisoformat(deadline_value)
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   arrival_deadline = timezone.make_aware(
                       datetime.combine(arrival_date, time.min),
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:127 Mutant #65`

  ```diff
  @@ -124,7 +124,7 @@
                   'cargo': cargo,
                   'deadline_value': deadline_value,
                   'deadline_error': deadline_error,
  -                'action': f'/admin/cargo/{tracking_id}/deadline/',
  +                'XXactionXX': f'/admin/cargo/{tracking_id}/deadline/',
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:127 Mutant #66`

  ```diff
  @@ -124,7 +124,7 @@
                   'cargo': cargo,
                   'deadline_value': deadline_value,
                   'deadline_error': deadline_error,
  -                'action': f'/admin/cargo/{tracking_id}/deadline/',
  +                'action': f'XX/admin/cargo/{tracking_id}/deadline/XX',
               },
           )
  ```

