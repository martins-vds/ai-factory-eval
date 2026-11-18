# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.774, threshold 0.8, killed 48, survived 14. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:38 Mutant #12`

  ```diff
  @@ -35,7 +35,7 @@
       def change_destination(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            return render(request, 'booking/dialogs/not_found.html', status=404)
  +            return render(request, 'XXbooking/dialogs/not_found.htmlXX', status=404)
           origin = cargo.route_specification.origin
           destination = cargo.route_specification.destination
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:38 Mutant #13`

  ```diff
  @@ -35,7 +35,7 @@
       def change_destination(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            return render(request, 'booking/dialogs/not_found.html', status=404)
  +            return render(request, 'booking/dialogs/not_found.html', status=405)
           origin = cargo.route_specification.origin
           destination = cargo.route_specification.destination
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:55 Mutant #28`

  ```diff
  @@ -52,7 +52,7 @@
                   {'cargo': cargo, 'destinations': locations},
               )
           if request.method != 'POST':
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['XXGETXX', 'POST'])
           destination_value = request.POST.get('destination', '')
           selected_destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:55 Mutant #29`

  ```diff
  @@ -52,7 +52,7 @@
                   {'cargo': cargo, 'destinations': locations},
               )
           if request.method != 'POST':
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['GET', 'XXPOSTXX'])
           destination_value = request.POST.get('destination', '')
           selected_destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:57 Mutant #31`

  ```diff
  @@ -54,7 +54,7 @@
           if request.method != 'POST':
               return HttpResponseNotAllowed(['GET', 'POST'])
  -        destination_value = request.POST.get('destination', '')
  +        destination_value = request.POST.get('destination', 'XXXX')
           selected_destination = next(
               (
                   location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:71 Mutant #37`

  ```diff
  @@ -68,7 +68,7 @@
                   request,
                   'booking/dialogs/destination.html',
                   {
  -                    'cargo': cargo,
  +                    'XXcargoXX': cargo,
                       'destinations': locations,
                       'destination_value': destination_value,
                       'destination_error': 'Select a valid destination.',
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:72 Mutant #38`

  ```diff
  @@ -69,7 +69,7 @@
                   'booking/dialogs/destination.html',
                   {
                       'cargo': cargo,
  -                    'destinations': locations,
  +                    'XXdestinationsXX': locations,
                       'destination_value': destination_value,
                       'destination_error': 'Select a valid destination.',
                   },
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:73 Mutant #39`

  ```diff
  @@ -70,7 +70,7 @@
                   {
                       'cargo': cargo,
                       'destinations': locations,
  -                    'destination_value': destination_value,
  +                    'XXdestination_valueXX': destination_value,
                       'destination_error': 'Select a valid destination.',
                   },
               )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:74 Mutant #41`

  ```diff
  @@ -71,7 +71,7 @@
                       'cargo': cargo,
                       'destinations': locations,
                       'destination_value': destination_value,
  -                    'destination_error': 'Select a valid destination.',
  +                    'destination_error': 'XXSelect a valid destination.XX',
                   },
               )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:88 Mutant #52`

  ```diff
  @@ -85,7 +85,7 @@
           if request.method == 'GET':
               return render(request, 'booking/dialogs/deadline.html', {'cargo': cargo})
           if request.method != 'POST':
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['XXGETXX', 'POST'])
           deadline_value = request.POST.get('deadline', '')
           try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:88 Mutant #53`

  ```diff
  @@ -85,7 +85,7 @@
           if request.method == 'GET':
               return render(request, 'booking/dialogs/deadline.html', {'cargo': cargo})
           if request.method != 'POST':
  -            return HttpResponseNotAllowed(['GET', 'POST'])
  +            return HttpResponseNotAllowed(['GET', 'XXPOSTXX'])
           deadline_value = request.POST.get('deadline', '')
           try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:90 Mutant #55`

  ```diff
  @@ -87,7 +87,7 @@
           if request.method != 'POST':
               return HttpResponseNotAllowed(['GET', 'POST'])
  -        deadline_value = request.POST.get('deadline', '')
  +        deadline_value = request.POST.get('deadline', 'XXXX')
           try:
               deadline = date.fromisoformat(deadline_value)
           except ValueError:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:98 Mutant #59`

  ```diff
  @@ -95,7 +95,7 @@
                   request,
                   'booking/dialogs/deadline.html',
                   {
  -                    'cargo': cargo,
  +                    'XXcargoXX': cargo,
                       'deadline_value': deadline_value,
                       'deadline_error': 'Enter a valid arrival deadline.',
                   },
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:100 Mutant #62`

  ```diff
  @@ -97,7 +97,7 @@
                   {
                       'cargo': cargo,
                       'deadline_value': deadline_value,
  -                    'deadline_error': 'Enter a valid arrival deadline.',
  +                    'deadline_error': 'XXEnter a valid arrival deadline.XX',
                   },
               )
  ```

