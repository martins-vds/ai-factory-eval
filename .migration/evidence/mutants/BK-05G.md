# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `6348f858891024d9bfc2ae05d30336a1bf9f2a12`): score 0.750, threshold 0.8, killed 42, survived 14. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:39 Mutant #13`

  ```diff
  @@ -36,7 +36,7 @@
               for location in list_shipping_locations()
               if location != origin and location != current_destination
           ]
  -        destination_value = request.POST.get('destination', '')
  +        destination_value = request.POST.get('destination', 'XXXX')
           selected_destination = next(
               (location for location in destinations if location.unlocode.value == destination_value),
               None,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:44 Mutant #17`

  ```diff
  @@ -41,7 +41,7 @@
               (location for location in destinations if location.unlocode.value == destination_value),
               None,
           )
  -        destination_error = ''
  +        destination_error = 'XXXX'
           if request.method == 'POST':
               if selected_destination is None:
                   destination_error = 'Select a valid destination.'
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:44 Mutant #18`

  ```diff
  @@ -41,7 +41,7 @@
               (location for location in destinations if location.unlocode.value == destination_value),
               None,
           )
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               if selected_destination is None:
                   destination_error = 'Select a valid destination.'
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:47 Mutant #22`

  ```diff
  @@ -44,7 +44,7 @@
           destination_error = ''
           if request.method == 'POST':
               if selected_destination is None:
  -                destination_error = 'Select a valid destination.'
  +                destination_error = 'XXSelect a valid destination.XX'
               else:
                   try:
                       specification.change_destination(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:59 Mutant #28`

  ```diff
  @@ -56,7 +56,7 @@
                   response = HttpResponse()
                   response['HX-Redirect'] = '/admin/dashboard/'
                   return response
  -        elif selected_destination is None and destinations:
  +        elif selected_destination is not None and destinations:
               selected_destination = destinations[0]
           return render(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:59 Mutant #29`

  ```diff
  @@ -56,7 +56,7 @@
                   response = HttpResponse()
                   response['HX-Redirect'] = '/admin/dashboard/'
                   return response
  -        elif selected_destination is None and destinations:
  +        elif selected_destination is None or destinations:
               selected_destination = destinations[0]
           return render(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:60 Mutant #30`

  ```diff
  @@ -57,7 +57,7 @@
                   response['HX-Redirect'] = '/admin/dashboard/'
                   return response
           elif selected_destination is None and destinations:
  -            selected_destination = destinations[0]
  +            selected_destination = destinations[1]
           return render(
               request,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:60 Mutant #31`

  ```diff
  @@ -57,7 +57,7 @@
                   response['HX-Redirect'] = '/admin/dashboard/'
                   return response
           elif selected_destination is None and destinations:
  -            selected_destination = destinations[0]
  +            selected_destination = None
           return render(
               request,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:67 Mutant #34`

  ```diff
  @@ -64,7 +64,7 @@
               'booking/dialogs/destination.html',
               {
                   'cargo': cargo,
  -                'destinations': destinations,
  +                'XXdestinationsXX': destinations,
                   'selected_destination': selected_destination,
                   'destination_error': destination_error,
                   'destination_value': destination_value,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:68 Mutant #35`

  ```diff
  @@ -65,7 +65,7 @@
               {
                   'cargo': cargo,
                   'destinations': destinations,
  -                'selected_destination': selected_destination,
  +                'XXselected_destinationXX': selected_destination,
                   'destination_error': destination_error,
                   'destination_value': destination_value,
               },
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:70 Mutant #37`

  ```diff
  @@ -67,7 +67,7 @@
                   'destinations': destinations,
                   'selected_destination': selected_destination,
                   'destination_error': destination_error,
  -                'destination_value': destination_value,
  +                'XXdestination_valueXX': destination_value,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:90 Mutant #42`

  ```diff
  @@ -87,7 +87,7 @@
               'arrival_deadline',
               cargo.route_specification.arrival_deadline.date().isoformat(),
           )
  -        deadline_error = ''
  +        deadline_error = 'XXXX'
           if request.method == 'POST':
               try:
                   arrival_date = date.fromisoformat(deadline_value)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:90 Mutant #43`

  ```diff
  @@ -87,7 +87,7 @@
               'arrival_deadline',
               cargo.route_specification.arrival_deadline.date().isoformat(),
           )
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               try:
                   arrival_date = date.fromisoformat(deadline_value)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:95 Mutant #47`

  ```diff
  @@ -92,7 +92,7 @@
               try:
                   arrival_date = date.fromisoformat(deadline_value)
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   try:
                       specification.change_deadline(
  ```

