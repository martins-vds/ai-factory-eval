# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.673, threshold 0.8, killed 35, survived 17. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:22 Mutant #3`

  ```diff
  @@ -19,7 +19,7 @@
       Callable[[HttpRequest, str], HttpResponse],
       Callable[[HttpRequest, str], HttpResponse],
   ]:
  -    @require_http_methods(['GET', 'POST'])
  +
       def change_destination(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo_tracking_id = TrackingId(tracking_id)
           cargo = cargo_repository.find(cargo_tracking_id)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:27 Mutant #7`

  ```diff
  @@ -24,7 +24,7 @@
           cargo_tracking_id = TrackingId(tracking_id)
           cargo = cargo_repository.find(cargo_tracking_id)
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           destinations = [
               location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:35 Mutant #10`

  ```diff
  @@ -32,7 +32,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        error = ''
  +        error = 'XXXX'
           if request.method == 'POST':
               destination = next(
                   (
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:35 Mutant #11`

  ```diff
  @@ -32,7 +32,7 @@
               if location
               not in (cargo.route_specification.origin, cargo.route_specification.destination)
           ]
  -        error = ''
  +        error = None
           if request.method == 'POST':
               destination = next(
                   (
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:46 Mutant #18`

  ```diff
  @@ -43,7 +43,7 @@
                   None,
               )
               if destination is None:
  -                error = 'Select a valid destination.'
  +                error = 'XXSelect a valid destination.XX'
               else:
                   try:
                       specification.change_destination(cargo_tracking_id, destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:46 Mutant #19`

  ```diff
  @@ -43,7 +43,7 @@
                   None,
               )
               if destination is None:
  -                error = 'Select a valid destination.'
  +                error = None
               else:
                   try:
                       specification.change_destination(cargo_tracking_id, destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:59 Mutant #22`

  ```diff
  @@ -56,7 +56,7 @@
               'booking/dialogs/destination.html',
               {
                   'cargo': cargo,
  -                'destinations': destinations,
  +                'XXdestinationsXX': destinations,
                   'error': error,
                   'form_url': request.path,
               },
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:60 Mutant #23`

  ```diff
  @@ -57,7 +57,7 @@
               {
                   'cargo': cargo,
                   'destinations': destinations,
  -                'error': error,
  +                'XXerrorXX': error,
                   'form_url': request.path,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:61 Mutant #24`

  ```diff
  @@ -58,7 +58,7 @@
                   'cargo': cargo,
                   'destinations': destinations,
                   'error': error,
  -                'form_url': request.path,
  +                'XXform_urlXX': request.path,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:65 Mutant #27`

  ```diff
  @@ -62,7 +62,6 @@
               },
           )
  -    @require_http_methods(['GET', 'POST'])
       def change_deadline(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo_tracking_id = TrackingId(tracking_id)
           cargo = cargo_repository.find(cargo_tracking_id)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:70 Mutant #31`

  ```diff
  @@ -67,7 +67,7 @@
           cargo_tracking_id = TrackingId(tracking_id)
           cargo = cargo_repository.find(cargo_tracking_id)
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           error = ''
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:73 Mutant #33`

  ```diff
  @@ -70,7 +70,7 @@
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = 'XXXX'
           if request.method == 'POST':
               deadline_value = request.POST.get('arrival_deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:73 Mutant #34`

  ```diff
  @@ -70,7 +70,7 @@
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('arrival_deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:75 Mutant #38`

  ```diff
  @@ -72,7 +72,7 @@
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           error = ''
           if request.method == 'POST':
  -            deadline_value = request.POST.get('arrival_deadline', '')
  +            deadline_value = request.POST.get('arrival_deadline', 'XXXX')
               try:
                   deadline = datetime.combine(
                       date.fromisoformat(deadline_value),
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:83 Mutant #41`

  ```diff
  @@ -80,7 +80,7 @@
                       tzinfo=UTC,
                   )
               except ValueError:
  -                error = 'Enter a valid arrival deadline.'
  +                error = 'XXEnter a valid arrival deadline.XX'
               else:
                   try:
                       specification.change_deadline(cargo_tracking_id, deadline)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:95 Mutant #44`

  ```diff
  @@ -92,7 +92,7 @@
               request,
               'booking/dialogs/deadline.html',
               {
  -                'cargo': cargo,
  +                'XXcargoXX': cargo,
                   'deadline_value': deadline_value,
                   'error': error,
                   'form_url': request.path,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:98 Mutant #47`

  ```diff
  @@ -95,7 +95,7 @@
                   'cargo': cargo,
                   'deadline_value': deadline_value,
                   'error': error,
  -                'form_url': request.path,
  +                'XXform_urlXX': request.path,
               },
           )
  ```

