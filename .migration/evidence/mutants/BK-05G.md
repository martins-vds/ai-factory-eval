# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.845, threshold 0.8, killed 60, survived 11. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:28 Mutant #9`

  ```diff
  @@ -25,7 +25,7 @@
               cargo.route_specification.origin,
               cargo.route_specification.destination,
           )
  -        selected_destination = request.POST.get('destination', '')
  +        selected_destination = request.POST.get('destination', 'XXXX')
           error = ''
           if request.method == 'POST':
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:29 Mutant #12`

  ```diff
  @@ -26,7 +26,7 @@
               cargo.route_specification.destination,
           )
           selected_destination = request.POST.get('destination', '')
  -        error = ''
  +        error = None
           if request.method == 'POST':
               destination = next(
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:41 Mutant #18`

  ```diff
  @@ -38,7 +38,7 @@
                   None,
               )
               if destination is None:
  -                error = 'Select a valid destination.'
  +                error = 'XXSelect a valid destination.XX'
               else:
                   cargo_specification.change_destination(TrackingId(tracking_id), destination)
                   return _dialog_completed(request)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:52 Mutant #24`

  ```diff
  @@ -49,7 +49,7 @@
               {
                   'action_url': f'/admin/cargo/{tracking_id}/destination/',
                   'cargo': cargo,
  -                'destinations': destinations,
  +                'XXdestinationsXX': destinations,
                   'selected_destination': selected_destination,
                   'error': error,
               },
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:53 Mutant #25`

  ```diff
  @@ -50,7 +50,7 @@
                   'action_url': f'/admin/cargo/{tracking_id}/destination/',
                   'cargo': cargo,
                   'destinations': destinations,
  -                'selected_destination': selected_destination,
  +                'XXselected_destinationXX': selected_destination,
                   'error': error,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:63 Mutant #35`

  ```diff
  @@ -60,7 +60,7 @@
               return HttpResponseNotAllowed(['GET', 'POST'])
           cargo = _get_cargo(cargo_dashboard, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        error = ''
  +        error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:70 Mutant #42`

  ```diff
  @@ -67,7 +67,7 @@
               try:
                   deadline = date.fromisoformat(deadline_value)
               except (TypeError, ValueError):
  -                error = 'Enter a valid arrival deadline.'
  +                error = 'XXEnter a valid arrival deadline.XX'
               else:
                   cargo_specification.change_deadline(
                       TrackingId(tracking_id),
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:95 Mutant #52`

  ```diff
  @@ -92,7 +92,7 @@
   def _get_cargo(cargo_dashboard: CargoDashboard, tracking_id: str) -> Cargo:
       cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       return cargo
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:112 Mutant #58`

  ```diff
  @@ -109,7 +109,7 @@
       context['dialog_type'] = dialog_type
       template = (
           'booking/dialogs/dialog.html'
  -        if request.headers.get('HX-Request') == 'true'
  +        if request.headers.get('XXHX-RequestXX') == 'true'
           else f'booking/dialogs/{dialog_type}.html'
       )
       return render(request, template, context)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:112 Mutant #59`

  ```diff
  @@ -109,7 +109,7 @@
       context['dialog_type'] = dialog_type
       template = (
           'booking/dialogs/dialog.html'
  -        if request.headers.get('HX-Request') == 'true'
  +        if request.headers.get('HX-Request') != 'true'
           else f'booking/dialogs/{dialog_type}.html'
       )
       return render(request, template, context)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:112 Mutant #60`

  ```diff
  @@ -109,7 +109,7 @@
       context['dialog_type'] = dialog_type
       template = (
           'booking/dialogs/dialog.html'
  -        if request.headers.get('HX-Request') == 'true'
  +        if request.headers.get('HX-Request') == 'XXtrueXX'
           else f'booking/dialogs/{dialog_type}.html'
       )
       return render(request, template, context)
  ```

