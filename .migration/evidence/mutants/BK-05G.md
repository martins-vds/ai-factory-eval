# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.759, threshold 0.8, killed 60, survived 19. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:26 Mutant #3`

  ```diff
  @@ -23,7 +23,7 @@
       def find_cargo(tracking_id: str) -> Cargo:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           return cargo
       def complete_dialog(request: HttpRequest) -> HttpResponse:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:31 Mutant #7`

  ```diff
  @@ -28,7 +28,7 @@
       def complete_dialog(request: HttpRequest) -> HttpResponse:
           if request.headers.get('HX-Request') != 'true':
  -            return redirect('/admin/dashboard/')
  +            return redirect('XX/admin/dashboard/XX')
           cargos = cargo_dashboard.get_dashboard()
           return render(
               request,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:55 Mutant #25`

  ```diff
  @@ -52,7 +52,7 @@
               if location.unlocode not in {origin.unlocode, current_destination.unlocode}
           ]
           return {
  -            'tracking_id': tracking_id,
  +            'XXtracking_idXX': tracking_id,
               'origin': origin,
               'current_destination': current_destination,
               'destinations': destinations,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:59 Mutant #29`

  ```diff
  @@ -56,7 +56,7 @@
               'origin': origin,
               'current_destination': current_destination,
               'destinations': destinations,
  -            'error': '',
  +            'XXerrorXX': '',
               'action_url': f'/admin/cargo/{tracking_id}/destination/',
           }
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:59 Mutant #30`

  ```diff
  @@ -56,7 +56,7 @@
               'origin': origin,
               'current_destination': current_destination,
               'destinations': destinations,
  -            'error': '',
  +            'error': 'XXXX',
               'action_url': f'/admin/cargo/{tracking_id}/destination/',
           }
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:60 Mutant #31`

  ```diff
  @@ -57,7 +57,7 @@
               'current_destination': current_destination,
               'destinations': destinations,
               'error': '',
  -            'action_url': f'/admin/cargo/{tracking_id}/destination/',
  +            'XXaction_urlXX': f'/admin/cargo/{tracking_id}/destination/',
           }
       @require_http_methods(['GET', 'POST'])
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:60 Mutant #32`

  ```diff
  @@ -57,7 +57,7 @@
               'current_destination': current_destination,
               'destinations': destinations,
               'error': '',
  -            'action_url': f'/admin/cargo/{tracking_id}/destination/',
  +            'action_url': f'XX/admin/cargo/{tracking_id}/destination/XX',
           }
       @require_http_methods(['GET', 'POST'])
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:63 Mutant #35`

  ```diff
  @@ -60,7 +60,6 @@
               'action_url': f'/admin/cargo/{tracking_id}/destination/',
           }
  -    @require_http_methods(['GET', 'POST'])
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = find_cargo(tracking_id)
           context = destination_context(cargo, tracking_id)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:68 Mutant #41`

  ```diff
  @@ -65,7 +65,7 @@
           cargo = find_cargo(tracking_id)
           context = destination_context(cargo, tracking_id)
           if request.method == 'POST':
  -            selected_code = request.POST.get('destination', '')
  +            selected_code = request.POST.get('destination', 'XXXX')
               destination = next(
                   (
                       location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:78 Mutant #48`

  ```diff
  @@ -75,7 +75,7 @@
                   None,
               )
               if destination is None:
  -                context['error'] = 'Select a valid destination.'
  +                context['error'] = 'XXSelect a valid destination.XX'
                   context['selected_destination'] = selected_code
                   return render_dialog_error(request, 'booking/dialogs/destination.html', context)
               cargo_specification.change_destination(TrackingId(tracking_id), destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:79 Mutant #50`

  ```diff
  @@ -76,7 +76,7 @@
               )
               if destination is None:
                   context['error'] = 'Select a valid destination.'
  -                context['selected_destination'] = selected_code
  +                context['XXselected_destinationXX'] = selected_code
                   return render_dialog_error(request, 'booking/dialogs/destination.html', context)
               cargo_specification.change_destination(TrackingId(tracking_id), destination)
               return complete_dialog(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:79 Mutant #51`

  ```diff
  @@ -76,7 +76,7 @@
               )
               if destination is None:
                   context['error'] = 'Select a valid destination.'
  -                context['selected_destination'] = selected_code
  +                context['selected_destination'] = None
                   return render_dialog_error(request, 'booking/dialogs/destination.html', context)
               cargo_specification.change_destination(TrackingId(tracking_id), destination)
               return complete_dialog(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:85 Mutant #56`

  ```diff
  @@ -82,7 +82,6 @@
               return complete_dialog(request)
           return render(request, 'booking/dialogs/destination.html', context)
  -    @require_http_methods(['GET', 'POST'])
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = find_cargo(tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:89 Mutant #59`

  ```diff
  @@ -86,7 +86,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = find_cargo(tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = 'XXXX'
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:89 Mutant #60`

  ```diff
  @@ -86,7 +86,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = find_cargo(tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
               try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:91 Mutant #64`

  ```diff
  @@ -88,7 +88,7 @@
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           error = ''
           if request.method == 'POST':
  -            deadline_value = request.POST.get('deadline', '')
  +            deadline_value = request.POST.get('deadline', 'XXXX')
               try:
                   deadline_date = datetime.strptime(deadline_value, '%Y-%m-%d').date()
               except ValueError:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:95 Mutant #68`

  ```diff
  @@ -92,7 +92,7 @@
               try:
                   deadline_date = datetime.strptime(deadline_value, '%Y-%m-%d').date()
               except ValueError:
  -                error = 'Enter a valid arrival deadline.'
  +                error = 'XXEnter a valid arrival deadline.XX'
               else:
                   deadline = datetime.combine(deadline_date, time.min, tzinfo=UTC)
                   cargo_specification.change_deadline(TrackingId(tracking_id), deadline)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:105 Mutant #75`

  ```diff
  @@ -102,7 +102,7 @@
               'destination': cargo.route_specification.destination,
               'deadline_value': deadline_value,
               'error': error,
  -            'action_url': f'/admin/cargo/{tracking_id}/deadline/',
  +            'XXaction_urlXX': f'/admin/cargo/{tracking_id}/deadline/',
           }
           if error:
               return render_dialog_error(request, 'booking/dialogs/deadline.html', context)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:105 Mutant #76`

  ```diff
  @@ -102,7 +102,7 @@
               'destination': cargo.route_specification.destination,
               'deadline_value': deadline_value,
               'error': error,
  -            'action_url': f'/admin/cargo/{tracking_id}/deadline/',
  +            'action_url': f'XX/admin/cargo/{tracking_id}/deadline/XX',
           }
           if error:
               return render_dialog_error(request, 'booking/dialogs/deadline.html', context)
  ```

