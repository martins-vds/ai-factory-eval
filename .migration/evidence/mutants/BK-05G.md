# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.778, threshold 0.8, killed 49, survived 14. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

- `src/cargotracker/booking/interfaces/dialogs/views.py:40 Mutant #17`

  ```diff
  @@ -37,7 +37,7 @@
       def update_response(request: HttpRequest) -> HttpResponse:
           if request.headers.get('HX-Request') == 'true':
               return refreshed_table(request)
  -        return redirect('/admin/dashboard/')
  +        return redirect('XX/admin/dashboard/XX')
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'POST'}:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:44 Mutant #21`

  ```diff
  @@ -41,7 +41,7 @@
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'POST'}:
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['XXGETXX', 'POST'])
           cargo = find_cargo(tracking_id)
           specification = cargo.route_specification
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:44 Mutant #22`

  ```diff
  @@ -41,7 +41,7 @@
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'POST'}:
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['GET', 'XXPOSTXX'])
           cargo = find_cargo(tracking_id)
           specification = cargo.route_specification
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:53 Mutant #27`

  ```diff
  @@ -50,7 +50,7 @@
               for location in list_shipping_locations()
               if location not in {specification.origin, specification.destination}
           ]
  -        destination_error = ''
  +        destination_error = 'XXXX'
           if request.method == 'POST':
               selected_code = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:53 Mutant #28`

  ```diff
  @@ -50,7 +50,7 @@
               for location in list_shipping_locations()
               if location not in {specification.origin, specification.destination}
           ]
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               selected_code = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:56 Mutant #32`

  ```diff
  @@ -53,7 +53,7 @@
           destination_error = ''
           if request.method == 'POST':
  -            selected_code = request.POST.get('destination', '')
  +            selected_code = request.POST.get('destination', 'XXXX')
               destination = next(
                   (location for location in destinations if location.unlocode.value == selected_code),
                   None,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:62 Mutant #37`

  ```diff
  @@ -59,7 +59,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = 'XXSelect a valid destination.XX'
               else:
                   try:
                       cargo_specification.change_destination(cargo.tracking_id, destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:82 Mutant #46`

  ```diff
  @@ -79,7 +79,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'POST'}:
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['XXGETXX', 'POST'])
           cargo = find_cargo(tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:82 Mutant #47`

  ```diff
  @@ -79,7 +79,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'POST'}:
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['GET', 'XXPOSTXX'])
           cargo = find_cargo(tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:86 Mutant #50`

  ```diff
  @@ -83,7 +83,7 @@
           cargo = find_cargo(tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = 'XXXX'
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:86 Mutant #51`

  ```diff
  @@ -83,7 +83,7 @@
           cargo = find_cargo(tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:89 Mutant #55`

  ```diff
  @@ -86,7 +86,7 @@
           deadline_error = ''
           if request.method == 'POST':
  -            deadline_value = request.POST.get('deadline', '')
  +            deadline_value = request.POST.get('deadline', 'XXXX')
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:93 Mutant #58`

  ```diff
  @@ -90,7 +90,7 @@
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   try:
                       cargo_specification.change_deadline(
  ```

