# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.759, threshold 0.8, killed 41, survived 13. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:17 Mutant #3`

  ```diff
  @@ -14,7 +14,7 @@
   def _find_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
       cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       return cargo
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:23 Mutant #7`

  ```diff
  @@ -20,7 +20,7 @@
   def _render_not_routed_table(request: HttpRequest, cargo_dashboard: CargoDashboard) -> HttpResponse:
       if request.headers.get('HX-Request') != 'true':
  -        return redirect('/admin/dashboard/')
  +        return redirect('XX/admin/dashboard/XX')
       response = render(
           request,
           'booking/dashboard/not_routed_table.html',
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:51 Mutant #22`

  ```diff
  @@ -48,7 +48,7 @@
                   cargo.route_specification.destination,
               )
           ]
  -        destination_value = request.POST.get('destination', '')
  +        destination_value = request.POST.get('destination', 'XXXX')
           destination_error = ''
           if request.method == 'POST':
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:52 Mutant #24`

  ```diff
  @@ -49,7 +49,7 @@
               )
           ]
           destination_value = request.POST.get('destination', '')
  -        destination_error = ''
  +        destination_error = 'XXXX'
           if request.method == 'POST':
               destination = next(
                   (
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:52 Mutant #25`

  ```diff
  @@ -49,7 +49,7 @@
               )
           ]
           destination_value = request.POST.get('destination', '')
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination = next(
                   (
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:63 Mutant #31`

  ```diff
  @@ -60,7 +60,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Choose a valid destination.'
  +                destination_error = 'XXChoose a valid destination.XX'
               else:
                   try:
                       cargo_specification.change_destination(TrackingId(tracking_id), destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:75 Mutant #35`

  ```diff
  @@ -72,7 +72,7 @@
               'booking/dialogs/destination.html',
               {
                   'cargo': cargo,
  -                'destination_options': destination_options,
  +                'XXdestination_optionsXX': destination_options,
                   'destination_value': destination_value,
                   'destination_error': destination_error,
               },
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:76 Mutant #36`

  ```diff
  @@ -73,7 +73,7 @@
               {
                   'cargo': cargo,
                   'destination_options': destination_options,
  -                'destination_value': destination_value,
  +                'XXdestination_valueXX': destination_value,
                   'destination_error': destination_error,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:91 Mutant #40`

  ```diff
  @@ -88,7 +88,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = 'XXXX'
           if request.method == 'POST':
               try:
                   arrival_date = datetime.strptime(request.POST.get('deadline', ''), '%Y-%m-%d')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:91 Mutant #41`

  ```diff
  @@ -88,7 +88,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               try:
                   arrival_date = datetime.strptime(request.POST.get('deadline', ''), '%Y-%m-%d')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:94 Mutant #45`

  ```diff
  @@ -91,7 +91,7 @@
           deadline_error = ''
           if request.method == 'POST':
               try:
  -                arrival_date = datetime.strptime(request.POST.get('deadline', ''), '%Y-%m-%d')
  +                arrival_date = datetime.strptime(request.POST.get('deadline', 'XXXX'), '%Y-%m-%d')
               except ValueError:
                   deadline_error = 'Enter a valid arrival deadline.'
               else:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:96 Mutant #48`

  ```diff
  @@ -93,7 +93,7 @@
               try:
                   arrival_date = datetime.strptime(request.POST.get('deadline', ''), '%Y-%m-%d')
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   try:
                       cargo_specification.change_deadline(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:111 Mutant #53`

  ```diff
  @@ -108,7 +108,7 @@
               'booking/dialogs/deadline.html',
               {
                   'cargo': cargo,
  -                'deadline_value': request.POST.get('deadline', deadline_value),
  +                'deadline_value': request.POST.get('XXdeadlineXX', deadline_value),
                   'deadline_error': deadline_error,
               },
           )
  ```

