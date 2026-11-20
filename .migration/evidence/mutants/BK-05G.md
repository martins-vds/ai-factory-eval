# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `b3b29def45ae6c8608e0427fddd7417d891deb42`): score 0.887, threshold 0.8, killed 47, survived 6. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:52 Mutant #19`

  ```diff
  @@ -49,7 +49,7 @@
   ) -> tuple[Callable[[HttpRequest, str], HttpResponse], Callable[[HttpRequest, str], HttpResponse]]:
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _find_cargo(cargo_dashboard, tracking_id)
  -        destination_error = ''
  +        destination_error = None
           destination_value = ''
           if request.method == 'POST':
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:53 Mutant #20`

  ```diff
  @@ -50,7 +50,7 @@
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           destination_error = ''
  -        destination_value = ''
  +        destination_value = 'XXXX'
           if request.method == 'POST':
               destination_value = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:53 Mutant #21`

  ```diff
  @@ -50,7 +50,7 @@
       def destination_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           destination_error = ''
  -        destination_value = ''
  +        destination_value = None
           if request.method == 'POST':
               destination_value = request.POST.get('destination', '')
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:56 Mutant #25`

  ```diff
  @@ -53,7 +53,7 @@
           destination_value = ''
           if request.method == 'POST':
  -            destination_value = request.POST.get('destination', '')
  +            destination_value = request.POST.get('destination', 'XXXX')
               destination = next(
                   (
                       location
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:77 Mutant #35`

  ```diff
  @@ -74,7 +74,7 @@
               {
                   'cargo': cargo,
                   'destinations': _destination_options(cargo, list_shipping_locations),
  -                'destination_value': destination_value,
  +                'XXdestination_valueXX': destination_value,
                   'destination_error': destination_error,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:85 Mutant #40`

  ```diff
  @@ -82,7 +82,7 @@
       def deadline_dialog(request: HttpRequest, tracking_id: str) -> HttpResponse:
           cargo = _find_cargo(cargo_dashboard, tracking_id)
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
  -        deadline_error = ''
  +        deadline_error = None
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```
