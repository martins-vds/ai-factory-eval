# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.776, threshold 0.8, killed 45, survived 13. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:23 Mutant #2`

  ```diff
  @@ -20,7 +20,7 @@
       return render(
           request,
           'booking/dialogs/not_found.html',
  -        {'tracking_id': tracking_id},
  +        {'XXtracking_idXX': tracking_id},
           status=404,
       )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:33 Mutant #11`

  ```diff
  @@ -30,7 +30,7 @@
           response = HttpResponse()
           response['HX-Redirect'] = '/admin/dashboard/'
           return response
  -    return redirect('/admin/dashboard/')
  +    return redirect('XX/admin/dashboard/XX')
   def create_destination_dialog_view(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:41 Mutant #14`

  ```diff
  @@ -38,7 +38,7 @@
       cargo_specification: CargoSpecification,
       list_shipping_locations: Callable[[], list[Location]],
   ) -> Callable[[HttpRequest, str], HttpResponse]:
  -    @require_http_methods(['GET', 'POST'])
  +
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
           if cargo is None:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:54 Mutant #23`

  ```diff
  @@ -51,7 +51,7 @@
               if location != cargo.route_specification.origin
               and location != cargo.route_specification.destination
           ]
  -        error = ''
  +        error = 'XXXX'
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:54 Mutant #24`

  ```diff
  @@ -51,7 +51,7 @@
               if location != cargo.route_specification.origin
               and location != cargo.route_specification.destination
           ]
  -        error = ''
  +        error = None
           if request.method == 'POST':
               destination_code = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:57 Mutant #28`

  ```diff
  @@ -54,7 +54,7 @@
           error = ''
           if request.method == 'POST':
  -            destination_code = request.POST.get('destination', '')
  +            destination_code = request.POST.get('destination', 'XXXX')
               destination = next(
                   (
                       location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:67 Mutant #33`

  ```diff
  @@ -64,7 +64,7 @@
                   None,
               )
               if destination is None:
  -                error = 'Select a valid destination.'
  +                error = 'XXSelect a valid destination.XX'
               else:
                   cargo_specification.change_destination(cargo_tracking_id, destination)
                   return _dialog_success(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:77 Mutant #37`

  ```diff
  @@ -74,7 +74,7 @@
               'booking/dialogs/destination.html',
               {
                   'cargo': cargo,
  -                'available_destinations': available_destinations,
  +                'XXavailable_destinationsXX': available_destinations,
                   'error': error,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:89 Mutant #41`

  ```diff
  @@ -86,7 +86,7 @@
       cargo_dashboard: CargoDashboard,
       cargo_specification: CargoSpecification,
   ) -> Callable[[HttpRequest, str], HttpResponse]:
  -    @require_http_methods(['GET', 'POST'])
  +
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
           if cargo is None:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:95 Mutant #45`

  ```diff
  @@ -92,7 +92,7 @@
           if cargo is None:
               return _not_found_response(request, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = 'XXXX'
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:95 Mutant #46`

  ```diff
  @@ -92,7 +92,7 @@
           if cargo is None:
               return _not_found_response(request, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:98 Mutant #50`

  ```diff
  @@ -95,7 +95,7 @@
           error = ''
           if request.method == 'POST':
  -            deadline_value = request.POST.get('deadline', '')
  +            deadline_value = request.POST.get('deadline', 'XXXX')
               try:
                   arrival_deadline = date.fromisoformat(deadline_value)
               except ValueError:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:102 Mutant #53`

  ```diff
  @@ -99,7 +99,7 @@
               try:
                   arrival_deadline = date.fromisoformat(deadline_value)
               except ValueError:
  -                error = 'Enter a valid arrival deadline.'
  +                error = 'XXEnter a valid arrival deadline.XX'
               else:
                   cargo_specification.change_deadline(
                       TrackingId(tracking_id),
  ```

