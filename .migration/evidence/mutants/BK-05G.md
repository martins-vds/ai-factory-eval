# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.852, threshold 0.8, killed 69, survived 12. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:34 Mutant #12`

  ```diff
  @@ -31,7 +31,7 @@
       return {
           'cargo': cargo,
           'potential_destinations': potential_destinations,
  -        'destination_error': destination_error,
  +        'XXdestination_errorXX': destination_error,
       }
  ```
- `src/cargotracker/booking/interfaces/dialogs/views.py:42 Mutant #16`

  ```diff
  @@ -39,7 +39,7 @@
       return {
           'cargo': cargo,
           'deadline_value': cargo.route_specification.arrival_deadline.date().isoformat(),
  -        'deadline_error': deadline_error,
  +        'XXdeadline_errorXX': deadline_error,
       }
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:63 Mutant #27`

  ```diff
  @@ -60,7 +60,7 @@
   def _render_dialog(
       request: HttpRequest, template_name: str, context: dict[str, object]
   ) -> HttpResponse:
  -    if request.headers.get('HX-Request') == 'true':
  +    if request.headers.get('XXHX-RequestXX') == 'true':
           return render(request, template_name, {**context, 'is_dialog': True})
       return render(
           request,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:63 Mutant #29`

  ```diff
  @@ -60,7 +60,7 @@
   def _render_dialog(
       request: HttpRequest, template_name: str, context: dict[str, object]
   ) -> HttpResponse:
  -    if request.headers.get('HX-Request') == 'true':
  +    if request.headers.get('HX-Request') == 'XXtrueXX':
           return render(request, template_name, {**context, 'is_dialog': True})
       return render(
           request,
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:64 Mutant #31`

  ```diff
  @@ -61,7 +61,7 @@
       request: HttpRequest, template_name: str, context: dict[str, object]
   ) -> HttpResponse:
       if request.headers.get('HX-Request') == 'true':
  -        return render(request, template_name, {**context, 'is_dialog': True})
  +        return render(request, template_name, {**context, 'XXis_dialogXX': True})
       return render(
           request,
           'booking/dialogs/edit_page.html',
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:64 Mutant #32`

  ```diff
  @@ -61,7 +61,7 @@
       request: HttpRequest, template_name: str, context: dict[str, object]
   ) -> HttpResponse:
       if request.headers.get('HX-Request') == 'true':
  -        return render(request, template_name, {**context, 'is_dialog': True})
  +        return render(request, template_name, {**context, 'is_dialog': False})
       return render(
           request,
           'booking/dialogs/edit_page.html',
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:68 Mutant #36`

  ```diff
  @@ -65,7 +65,7 @@
       return render(
           request,
           'booking/dialogs/edit_page.html',
  -        {**context, 'dialog_template': template_name, 'is_dialog': False},
  +        {**context, 'dialog_template': template_name, 'XXis_dialogXX': False},
       )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:68 Mutant #37`

  ```diff
  @@ -65,7 +65,7 @@
       return render(
           request,
           'booking/dialogs/edit_page.html',
  -        {**context, 'dialog_template': template_name, 'is_dialog': False},
  +        {**context, 'dialog_template': template_name, 'is_dialog': True},
       )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:94 Mutant #56`

  ```diff
  @@ -91,7 +91,7 @@
           if request.method == 'GET':
               return _render_dialog(request, 'booking/dialogs/destination.html', context)
  -        destination_code = request.POST.get('destination', '')
  +        destination_code = request.POST.get('destination', 'XXXX')
           destination = next(
               (
                   location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:104 Mutant #62`

  ```diff
  @@ -101,7 +101,7 @@
               None,
           )
           if destination is None:
  -            context['destination_error'] = 'Select a valid destination.'
  +            context['destination_error'] = 'XXSelect a valid destination.XX'
               return _render_dialog(request, 'booking/dialogs/destination.html', context)
           try:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:123 Mutant #76`

  ```diff
  @@ -120,7 +120,7 @@
               return _render_dialog(request, 'booking/dialogs/deadline.html', context)
           try:
  -            deadline = date.fromisoformat(request.POST.get('deadline', ''))
  +            deadline = date.fromisoformat(request.POST.get('deadline', 'XXXX'))
           except ValueError:
               context['deadline_error'] = 'Enter a valid arrival deadline.'
               return _render_dialog(request, 'booking/dialogs/deadline.html', context)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:125 Mutant #79`

  ```diff
  @@ -122,7 +122,7 @@
           try:
               deadline = date.fromisoformat(request.POST.get('deadline', ''))
           except ValueError:
  -            context['deadline_error'] = 'Enter a valid arrival deadline.'
  +            context['deadline_error'] = 'XXEnter a valid arrival deadline.XX'
               return _render_dialog(request, 'booking/dialogs/deadline.html', context)
           try:
  ```
