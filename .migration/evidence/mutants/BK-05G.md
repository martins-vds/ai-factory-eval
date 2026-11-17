# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.739, threshold 0.8, killed 51, survived 18. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

- `src/cargotracker/booking/interfaces/dialogs/views.py:29 Mutant #13`

  ```diff
  @@ -26,7 +26,7 @@
   def _complete_dialog_update(request: HttpRequest) -> HttpResponse:
       if request.headers.get('HX-Request') == 'true':
           return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})
  -    return redirect('/admin/dashboard/')
  +    return redirect('XX/admin/dashboard/XX')
   def create_dialog_views(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:42 Mutant #17`

  ```diff
  @@ -39,7 +39,7 @@
   ]:
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'POST'}:
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['XXGETXX', 'POST'])
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           route_specification = cargo.route_specification
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:42 Mutant #18`

  ```diff
  @@ -39,7 +39,7 @@
   ]:
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'POST'}:
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['GET', 'XXPOSTXX'])
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           route_specification = cargo.route_specification
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:52 Mutant #24`

  ```diff
  @@ -49,7 +49,7 @@
               if location not in (route_specification.origin, route_specification.destination)
           ]
           destination_value = (
  -            request.POST.get('destination', '')
  +            request.POST.get('destination', 'XXXX')
               if request.method == 'POST'
               else (destinations[0].unlocode.value if destinations else '')
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:54 Mutant #28`

  ```diff
  @@ -51,7 +51,7 @@
           destination_value = (
               request.POST.get('destination', '')
               if request.method == 'POST'
  -            else (destinations[0].unlocode.value if destinations else '')
  +            else (destinations[0].unlocode.value if destinations else 'XXXX')
           )
           destination_error = ''
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:56 Mutant #31`

  ```diff
  @@ -53,7 +53,7 @@
               if request.method == 'POST'
               else (destinations[0].unlocode.value if destinations else '')
           )
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:68 Mutant #37`

  ```diff
  @@ -65,7 +65,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = 'XXSelect a valid destination.XX'
               else:
                   cargo_specification.change_destination(TrackingId(tracking_id), destination)
                   return _complete_dialog_update(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:91 Mutant #49`

  ```diff
  @@ -88,7 +88,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'POST'}:
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['XXGETXX', 'POST'])
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           deadline_value = (
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:91 Mutant #50`

  ```diff
  @@ -88,7 +88,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           if request.method not in {'GET', 'POST'}:
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['GET', 'XXPOSTXX'])
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           deadline_value = (
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:95 Mutant #53`

  ```diff
  @@ -92,7 +92,7 @@
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           deadline_value = (
  -            request.POST.get('deadline', '')
  +            request.POST.get('deadline', 'XXXX')
               if request.method == 'POST'
               else cargo.route_specification.arrival_deadline.date().isoformat()
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:99 Mutant #57`

  ```diff
  @@ -96,7 +96,7 @@
               if request.method == 'POST'
               else cargo.route_specification.arrival_deadline.date().isoformat()
           )
  -        deadline_error = ''
  +        deadline_error = 'XXXX'
           if request.method == 'POST':
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:99 Mutant #58`

  ```diff
  @@ -96,7 +96,7 @@
               if request.method == 'POST'
               else cargo.route_specification.arrival_deadline.date().isoformat()
           )
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:105 Mutant #62`

  ```diff
  @@ -102,7 +102,7 @@
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   cargo_specification.change_deadline(
                       TrackingId(tracking_id),
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:114 Mutant #64`

  ```diff
  @@ -111,7 +111,7 @@
                   return _complete_dialog_update(request)
           context = {
  -            'cargo': cargo,
  +            'XXcargoXX': cargo,
               'deadline_value': deadline_value,
               'deadline_error': deadline_error,
           }
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:123 Mutant #69`

  ```diff
  @@ -120,7 +120,7 @@
               _dialog_template(
                   request,
                   'booking/dialogs/_deadline_form.html',
  -                'booking/dialogs/deadline.html',
  +                'XXbooking/dialogs/deadline.htmlXX',
               ),
               context,
           )
  ```

