# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `69441c3a713bf54fcd5c5986d77603941a984e6d`): score 0.846, threshold 0.8, killed 44, survived 8. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

- `src/cargotracker/booking/interfaces/dialogs/views.py:44 Mutant #20`

  ```diff
  @@ -41,7 +41,7 @@
               location for location in locations if location.unlocode.value not in excluded_codes
           ]
           destination_value = request.POST.get('destination', '')
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:56 Mutant #26`

  ```diff
  @@ -53,7 +53,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = 'XXSelect a valid destination.XX'
               else:
                   try:
                       specification.change_destination(TrackingId(tracking_id), destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:70 Mutant #31`

  ```diff
  @@ -67,7 +67,7 @@
               {
                   'cargo': cargo,
                   'destinations': destinations,
  -                'destination_value': destination_value,
  +                'XXdestination_valueXX': destination_value,
                   'destination_error': destination_error,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:78 Mutant #35`

  ```diff
  @@ -75,7 +75,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           deadline_value = (
  -            request.POST.get('deadline', '')
  +            request.POST.get('deadline', 'XXXX')
               if request.method == 'POST'
               else cargo.route_specification.arrival_deadline.strftime('%Y-%m-%d')
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:82 Mutant #41`

  ```diff
  @@ -79,7 +79,7 @@
               if request.method == 'POST'
               else cargo.route_specification.arrival_deadline.strftime('%Y-%m-%d')
           )
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:89 Mutant #45`

  ```diff
  @@ -86,7 +86,7 @@
                   arrival_deadline = datetime.combine(date.fromisoformat(deadline_value), time.min)
               except ValueError:
                   deadline_error = (
  -                    'Choose an arrival deadline.'
  +                    'XXChoose an arrival deadline.XX'
                       if not deadline_value
                       else 'Enter a valid arrival deadline.'
                   )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:91 Mutant #47`

  ```diff
  @@ -88,7 +88,7 @@
                   deadline_error = (
                       'Choose an arrival deadline.'
                       if not deadline_value
  -                    else 'Enter a valid arrival deadline.'
  +                    else 'XXEnter a valid arrival deadline.XX'
                   )
               else:
                   try:
  ```

