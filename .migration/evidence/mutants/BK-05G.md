# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.709, threshold 0.8, killed 61, survived 25. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:16 Mutant #1`

  ```diff
  @@ -13,7 +13,7 @@
   def _not_found_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
  -    message = f'Cargo with tracking ID {tracking_id} not found.'
  +    message = f'XXCargo with tracking ID {tracking_id} not found.XX'
       if request.headers.get('HX-Request') == 'true':
           return render(
               request,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:31 Mutant #11`

  ```diff
  @@ -28,7 +28,7 @@
       cargo_dashboard: CargoDashboard,
       cargo_specification: CargoSpecification,
   ) -> Callable[[HttpRequest, str], HttpResponse]:
  -    @require_http_methods(['GET', 'POST'])
  +
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:38 Mutant #15`

  ```diff
  @@ -35,7 +35,7 @@
               return _not_found_dialog(request, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = 'XXXX'
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:38 Mutant #16`

  ```diff
  @@ -35,7 +35,7 @@
               return _not_found_dialog(request, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:40 Mutant #20`

  ```diff
  @@ -37,7 +37,7 @@
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           deadline_error = ''
           if request.method == 'POST':
  -            deadline_value = request.POST.get('deadline', '')
  +            deadline_value = request.POST.get('deadline', 'XXXX')
               try:
                   deadline = date.fromisoformat(deadline_value)
                   if deadline.isoformat() != deadline_value:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:46 Mutant #24`

  ```diff
  @@ -43,7 +43,7 @@
                   if deadline.isoformat() != deadline_value:
                       raise ValueError
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   cargo_specification.change_deadline(
                       cargo.tracking_id,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:54 Mutant #32`

  ```diff
  @@ -51,7 +51,7 @@
                   )
                   if request.headers.get('HX-Request') == 'true':
                       return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})
  -                return redirect('/admin/dashboard/')
  +                return redirect('XX/admin/dashboard/XX')
           context = {
               'cargo': cargo,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:60 Mutant #36`

  ```diff
  @@ -57,7 +57,7 @@
               'cargo': cargo,
               'deadline_value': deadline_value,
               'deadline_error': deadline_error,
  -            'tracking_id': tracking_id,
  +            'XXtracking_idXX': tracking_id,
           }
           template = (
               'booking/dialogs/_deadline_dialog.html'
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:64 Mutant #39`

  ```diff
  @@ -61,7 +61,7 @@
           }
           template = (
               'booking/dialogs/_deadline_dialog.html'
  -            if request.headers.get('HX-Request') == 'true'
  +            if request.headers.get('XXHX-RequestXX') == 'true'
               else 'booking/dialogs/deadline.html'
           )
           return render(request, template, context)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:64 Mutant #41`

  ```diff
  @@ -61,7 +61,7 @@
           }
           template = (
               'booking/dialogs/_deadline_dialog.html'
  -            if request.headers.get('HX-Request') == 'true'
  +            if request.headers.get('HX-Request') == 'XXtrueXX'
               else 'booking/dialogs/deadline.html'
           )
           return render(request, template, context)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:77 Mutant #46`

  ```diff
  @@ -74,7 +74,7 @@
       cargo_specification: CargoSpecification,
       list_shipping_locations: Callable[[], list[Location]],
   ) -> Callable[[HttpRequest, str], HttpResponse]:
  -    @require_http_methods(['GET', 'POST'])
  +
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:90 Mutant #53`

  ```diff
  @@ -87,7 +87,7 @@
               for location in list_shipping_locations()
               if location not in (origin, current_destination)
           ]
  -        destination_value = ''
  +        destination_value = 'XXXX'
           destination_error = ''
           if request.method == 'POST':
               destination_value = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:90 Mutant #54`

  ```diff
  @@ -87,7 +87,7 @@
               for location in list_shipping_locations()
               if location not in (origin, current_destination)
           ]
  -        destination_value = ''
  +        destination_value = None
           destination_error = ''
           if request.method == 'POST':
               destination_value = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:91 Mutant #55`

  ```diff
  @@ -88,7 +88,7 @@
               if location not in (origin, current_destination)
           ]
           destination_value = ''
  -        destination_error = ''
  +        destination_error = 'XXXX'
           if request.method == 'POST':
               destination_value = request.POST.get('destination', '')
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:91 Mutant #56`

  ```diff
  @@ -88,7 +88,7 @@
               if location not in (origin, current_destination)
           ]
           destination_value = ''
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination_value = request.POST.get('destination', '')
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:93 Mutant #60`

  ```diff
  @@ -90,7 +90,7 @@
           destination_value = ''
           destination_error = ''
           if request.method == 'POST':
  -            destination_value = request.POST.get('destination', '')
  +            destination_value = request.POST.get('destination', 'XXXX')
               destination = next(
                   (
                       location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:103 Mutant #65`

  ```diff
  @@ -100,7 +100,7 @@
                   None,
               )
               if destination is None:
  -                destination_error = 'Choose a valid destination.'
  +                destination_error = 'XXChoose a valid destination.XX'
               else:
                   cargo_specification.change_destination(cargo.tracking_id, destination)
                   if request.headers.get('HX-Request') == 'true':
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:108 Mutant #73`

  ```diff
  @@ -105,7 +105,7 @@
                   cargo_specification.change_destination(cargo.tracking_id, destination)
                   if request.headers.get('HX-Request') == 'true':
                       return HttpResponse(status=204, headers={'HX-Redirect': '/admin/dashboard/'})
  -                return redirect('/admin/dashboard/')
  +                return redirect('XX/admin/dashboard/XX')
           context = {
               'cargo': cargo,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:113 Mutant #76`

  ```diff
  @@ -110,7 +110,7 @@
           context = {
               'cargo': cargo,
               'current_destination': current_destination,
  -            'destination_value': destination_value,
  +            'XXdestination_valueXX': destination_value,
               'destination_error': destination_error,
               'locations': locations,
               'tracking_id': tracking_id,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:115 Mutant #78`

  ```diff
  @@ -112,7 +112,7 @@
               'current_destination': current_destination,
               'destination_value': destination_value,
               'destination_error': destination_error,
  -            'locations': locations,
  +            'XXlocationsXX': locations,
               'tracking_id': tracking_id,
           }
           template = (
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:116 Mutant #79`

  ```diff
  @@ -113,7 +113,7 @@
               'destination_value': destination_value,
               'destination_error': destination_error,
               'locations': locations,
  -            'tracking_id': tracking_id,
  +            'XXtracking_idXX': tracking_id,
           }
           template = (
               'booking/dialogs/_destination_dialog.html'
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:120 Mutant #82`

  ```diff
  @@ -117,7 +117,7 @@
           }
           template = (
               'booking/dialogs/_destination_dialog.html'
  -            if request.headers.get('HX-Request') == 'true'
  +            if request.headers.get('XXHX-RequestXX') == 'true'
               else 'booking/dialogs/destination.html'
           )
           return render(request, template, context)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:120 Mutant #83`

  ```diff
  @@ -117,7 +117,7 @@
           }
           template = (
               'booking/dialogs/_destination_dialog.html'
  -            if request.headers.get('HX-Request') == 'true'
  +            if request.headers.get('HX-Request') != 'true'
               else 'booking/dialogs/destination.html'
           )
           return render(request, template, context)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:120 Mutant #84`

  ```diff
  @@ -117,7 +117,7 @@
           }
           template = (
               'booking/dialogs/_destination_dialog.html'
  -            if request.headers.get('HX-Request') == 'true'
  +            if request.headers.get('HX-Request') == 'XXtrueXX'
               else 'booking/dialogs/destination.html'
           )
           return render(request, template, context)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:121 Mutant #85`

  ```diff
  @@ -118,7 +118,7 @@
           template = (
               'booking/dialogs/_destination_dialog.html'
               if request.headers.get('HX-Request') == 'true'
  -            else 'booking/dialogs/destination.html'
  +            else 'XXbooking/dialogs/destination.htmlXX'
           )
           return render(request, template, context)
  ```

