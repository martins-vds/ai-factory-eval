# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.954, threshold 0.8, killed 83, survived 4. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:26 Mutant #3`

  ```diff
  @@ -23,7 +23,7 @@
       def find_cargo(request: HttpRequest, tracking_id: str) -> Cargo | HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            message = f'Cargo with tracking ID {tracking_id} not found.'
  +            message = f'XXCargo with tracking ID {tracking_id} not found.XX'
               if request.headers.get('HX-Request') == 'true':
                   response = render(
                       request,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:89 Mutant #58`

  ```diff
  @@ -86,7 +86,7 @@
                   None,
               )
               if destination is None:
  -                context['error'] = 'Select a valid destination.'
  +                context['error'] = 'XXSelect a valid destination.XX'
                   return render_dialog_error(request, 'booking/dialogs/destination.html', context)
               cargo_specification.change_destination(TrackingId(tracking_id), destination)
               return complete_dialog(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:101 Mutant #68`

  ```diff
  @@ -98,7 +98,7 @@
           if isinstance(cargo, HttpResponse):
               return cargo
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:107 Mutant #76`

  ```diff
  @@ -104,7 +104,7 @@
               try:
                   deadline_date = datetime.strptime(deadline_value, '%Y-%m-%d').date()
               except ValueError:
  -                error = 'Enter a valid arrival deadline.'
  +                error = 'XXEnter a valid arrival deadline.XX'
               else:
                   deadline = datetime.combine(deadline_date, time.min, tzinfo=UTC)
                   cargo_specification.change_deadline(TrackingId(tracking_id), deadline)
  ```

