# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.722, threshold 0.8, killed 39, survived 15. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:35 Mutant #10`

  ```diff
  @@ -32,7 +32,7 @@
           response = HttpResponse()
           response['HX-Redirect'] = '/admin/dashboard/'
           return response
  -    return redirect('/admin/dashboard/')
  +    return redirect('XX/admin/dashboard/XX')
   def create_booking_dialog_views(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:49 Mutant #14`

  ```diff
  @@ -46,7 +46,7 @@
               return render(
                   request,
                   'booking/dialogs/not_found.html',
  -                {'tracking_id': tracking_id},
  +                {'XXtracking_idXX': tracking_id},
                   status=404,
               )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:54 Mutant #18`

  ```diff
  @@ -51,7 +51,7 @@
               )
           locations = _destination_options(list_shipping_locations(), cargo)
  -        selected_destination = request.POST.get('destination', '')
  +        selected_destination = request.POST.get('destination', 'XXXX')
           destination = next(
               (location for location in locations if location.unlocode.value == selected_destination),
               None,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:59 Mutant #22`

  ```diff
  @@ -56,7 +56,7 @@
               (location for location in locations if location.unlocode.value == selected_destination),
               None,
           )
  -        destination_error = ''
  +        destination_error = 'XXXX'
           if request.method == 'POST':
               if destination is None:
                   destination_error = 'Select an available destination.'
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:59 Mutant #23`

  ```diff
  @@ -56,7 +56,7 @@
               (location for location in locations if location.unlocode.value == selected_destination),
               None,
           )
  -        destination_error = ''
  +        destination_error = None
           if request.method == 'POST':
               if destination is None:
                   destination_error = 'Select an available destination.'
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:62 Mutant #27`

  ```diff
  @@ -59,7 +59,7 @@
           destination_error = ''
           if request.method == 'POST':
               if destination is None:
  -                destination_error = 'Select an available destination.'
  +                destination_error = 'XXSelect an available destination.XX'
               else:
                   cargo_specification.change_destination(cargo.tracking_id, destination)
                   return _completion_response(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:73 Mutant #32`

  ```diff
  @@ -70,7 +70,7 @@
               {
                   'cargo': cargo,
                   'locations': locations,
  -                'selected_destination': selected_destination,
  +                'XXselected_destinationXX': selected_destination,
                   'destination_error': destination_error,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:83 Mutant #36`

  ```diff
  @@ -80,7 +80,7 @@
           if cargo is None:
               return render(
                   request,
  -                'booking/dialogs/not_found.html',
  +                'XXbooking/dialogs/not_found.htmlXX',
                   {'tracking_id': tracking_id},
                   status=404,
               )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:84 Mutant #37`

  ```diff
  @@ -81,7 +81,7 @@
               return render(
                   request,
                   'booking/dialogs/not_found.html',
  -                {'tracking_id': tracking_id},
  +                {'XXtracking_idXX': tracking_id},
                   status=404,
               )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:85 Mutant #38`

  ```diff
  @@ -82,7 +82,7 @@
                   request,
                   'booking/dialogs/not_found.html',
                   {'tracking_id': tracking_id},
  -                status=404,
  +                status=405,
               )
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:89 Mutant #40`

  ```diff
  @@ -86,7 +86,7 @@
               )
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = 'XXXX'
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:89 Mutant #41`

  ```diff
  @@ -86,7 +86,7 @@
               )
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:91 Mutant #45`

  ```diff
  @@ -88,7 +88,7 @@
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           deadline_error = ''
           if request.method == 'POST':
  -            deadline_value = request.POST.get('deadline', '')
  +            deadline_value = request.POST.get('deadline', 'XXXX')
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:95 Mutant #48`

  ```diff
  @@ -92,7 +92,7 @@
               try:
                   deadline = date.fromisoformat(deadline_value)
               except ValueError:
  -                deadline_error = 'Enter a valid arrival deadline.'
  +                deadline_error = 'XXEnter a valid arrival deadline.XX'
               else:
                   arrival_deadline = timezone.make_aware(
                       datetime.combine(deadline, time.min),
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:107 Mutant #52`

  ```diff
  @@ -104,7 +104,7 @@
               request,
               'booking/dialogs/deadline.html',
               {
  -                'cargo': cargo,
  +                'XXcargoXX': cargo,
                   'deadline_value': deadline_value,
                   'deadline_error': deadline_error,
               },
  ```

