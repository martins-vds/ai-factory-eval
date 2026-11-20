# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `c6d033992ff59d8640efed62f3b53589e26bd69f`): score 0.887, threshold 0.8, killed 63, survived 8. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

