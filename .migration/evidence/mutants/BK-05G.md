# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `c6d033992ff59d8640efed62f3b53589e26bd69f`): score 0.789, threshold 0.8, killed 56, survived 15. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:21 Mutant #2`

  ```diff
  @@ -18,7 +18,7 @@
   def _dialog_template(request: HttpRequest, name: str) -> str:
  -    page_suffix = '' if request.headers.get('HX-Request') == 'true' else '_page'
  +    page_suffix = '' if request.headers.get('XXHX-RequestXX') == 'true' else '_page'
       return f'booking/dialogs/{name}{page_suffix}.html'
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:21 Mutant #4`

  ```diff
  @@ -18,7 +18,7 @@
   def _dialog_template(request: HttpRequest, name: str) -> str:
  -    page_suffix = '' if request.headers.get('HX-Request') == 'true' else '_page'
  +    page_suffix = '' if request.headers.get('HX-Request') == 'XXtrueXX' else '_page'
       return f'booking/dialogs/{name}{page_suffix}.html'
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:50 Mutant #22`

  ```diff
  @@ -47,7 +47,7 @@
       Callable[[HttpRequest, str], HttpResponse],
       Callable[[HttpRequest, str], HttpResponse],
   ]:
  -    @require_http_methods(['GET', 'POST'])
  +
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           if cargo is None:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:63 Mutant #29`

  ```diff
  @@ -60,7 +60,7 @@
               if location not in (route_specification.origin, route_specification.destination)
           ]
           destination_value = (
  -            request.POST.get('destination', '')
  +            request.POST.get('destination', 'XXXX')
               if request.method == 'POST'
               else (destinations[0].unlocode.value if destinations else '')
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:65 Mutant #32`

  ```diff
  @@ -62,7 +62,7 @@
           destination_value = (
               request.POST.get('destination', '')
               if request.method == 'POST'
  -            else (destinations[0].unlocode.value if destinations else '')
  +            else (destinations[1].unlocode.value if destinations else '')
           )
           destination_error = ''
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:65 Mutant #33`

  ```diff
  @@ -62,7 +62,7 @@
           destination_value = (
               request.POST.get('destination', '')
               if request.method == 'POST'
  -            else (destinations[0].unlocode.value if destinations else '')
  +            else (destinations[0].unlocode.value if destinations else 'XXXX')
           )
           destination_error = ''
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:67 Mutant #35`

  ```diff
  @@ -64,7 +64,7 @@
               if request.method == 'POST'
               else (destinations[0].unlocode.value if destinations else '')
           )
  -        destination_error = ''
  +        destination_error = 'XXXX'
           if request.method == 'POST':
               destination_by_code = {location.unlocode.value: location for location in destinations}
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:67 Mutant #36`

  ```diff
  @@ -64,7 +64,7 @@
               if request.method == 'POST'
               else (destinations[0].unlocode.value if destinations else '')
           )
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               destination_by_code = {location.unlocode.value: location for location in destinations}
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:73 Mutant #42`

  ```diff
  @@ -70,7 +70,7 @@
               destination_by_code = {location.unlocode.value: location for location in destinations}
               destination = destination_by_code.get(destination_value)
               if destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = 'XXSelect a valid destination.XX'
               else:
                   try:
                       cargo_specification.change_destination(TrackingId(tracking_id), destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:87 Mutant #47`

  ```diff
  @@ -84,7 +84,7 @@
               {
                   'cargo': cargo,
                   'destinations': destinations,
  -                'destination_value': destination_value,
  +                'XXdestination_valueXX': destination_value,
                   'destination_error': destination_error,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:92 Mutant #51`

  ```diff
  @@ -89,7 +89,6 @@
               },
           )
  -    @require_http_methods(['GET', 'POST'])
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           if cargo is None:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:99 Mutant #55`

  ```diff
  @@ -96,7 +96,7 @@
               return _not_found_response(request, tracking_id)
           deadline_value = (
  -            request.POST.get('deadline', '')
  +            request.POST.get('deadline', 'XXXX')
               if request.method == 'POST'
               else cargo.route_specification.arrival_deadline.date().isoformat()
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:103 Mutant #59`

  ```diff
  @@ -100,7 +100,7 @@
               if request.method == 'POST'
               else cargo.route_specification.arrival_deadline.date().isoformat()
           )
  -        deadline_error = ''
  +        deadline_error = 'XXXX'
           if request.method == 'POST':
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:103 Mutant #60`

  ```diff
  @@ -100,7 +100,7 @@
               if request.method == 'POST'
               else cargo.route_specification.arrival_deadline.date().isoformat()
           )
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:111 Mutant #65`

  ```diff
  @@ -108,7 +108,7 @@
                   if arrival_date.isoformat() != deadline_value:
                       raise ValueError
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   arrival_deadline = timezone.make_aware(datetime.combine(arrival_date, time.min))
                   try:
  ```

