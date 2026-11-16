# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.783, threshold 0.8, killed 36, survived 10. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:16 Mutant #3`

  ```diff
  @@ -13,7 +13,7 @@
   def _cargo_for_dialog(cargo_dashboard: CargoDashboard, tracking_id: str):
       cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       return cargo
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:23 Mutant #9`

  ```diff
  @@ -20,7 +20,7 @@
   def _complete_dialog(request: HttpRequest) -> HttpResponse:
       if request.headers.get('HX-Request') == 'true':
           return HttpResponse(headers={'HX-Trigger': 'cargoUpdated'})
  -    return redirect('/admin/dashboard/')
  +    return redirect('XX/admin/dashboard/XX')
   def create_destination_dialog_view(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:40 Mutant #14`

  ```diff
  @@ -37,7 +37,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        destination_error = ''
  +        destination_error = 'XXXX'
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:40 Mutant #15`

  ```diff
  @@ -37,7 +37,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:43 Mutant #19`

  ```diff
  @@ -40,7 +40,7 @@
           destination_error = ''
           if request.method == 'POST':
  -            destination_code = request.POST.get('destination', '')
  +            destination_code = request.POST.get('destination', 'XXXX')
               destination = next(
                   (
                       location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:53 Mutant #24`

  ```diff
  @@ -50,7 +50,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = 'XXSelect a valid destination.XX'
               else:
                   specification.change_destination(cargo.tracking_id, destination)
                   return _complete_dialog(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:78 Mutant #32`

  ```diff
  @@ -75,7 +75,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = 'XXXX'
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:78 Mutant #33`

  ```diff
  @@ -75,7 +75,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:81 Mutant #37`

  ```diff
  @@ -78,7 +78,7 @@
           deadline_error = ''
           if request.method == 'POST':
  -            deadline_value = request.POST.get('deadline', '')
  +            deadline_value = request.POST.get('deadline', 'XXXX')
               try:
                   deadline = datetime.strptime(deadline_value, '%Y-%m-%d').date()
               except ValueError:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:85 Mutant #41`

  ```diff
  @@ -82,7 +82,7 @@
               try:
                   deadline = datetime.strptime(deadline_value, '%Y-%m-%d').date()
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   specification.change_deadline(
                       cargo.tracking_id,
  ```

