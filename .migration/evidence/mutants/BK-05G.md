# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `b4373fca788d17c369e8b391a410a0bdde2d5765`): score 0.971, threshold 0.8, killed 66, survived 2. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:65 Mutant #32`

  ```diff
  @@ -62,7 +62,7 @@
               if location != route_specification.origin
               and location != route_specification.destination
           ]
  -        error = ''
  +        error = None
           if request.method == 'POST':
               destination_by_code = {location.unlocode.value: location for location in destinations}
               destination = destination_by_code.get(request.POST.get('destination'))
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:92 Mutant #53`

  ```diff
  @@ -89,7 +89,7 @@
           if request.method not in {'GET', 'POST'}:
               return HttpResponseNotAllowed(['GET', 'POST'])
           cargo_id, cargo = _cargo_for_dialog(cargo_dashboard, tracking_id)
  -        error = ''
  +        error = None
           deadline_value = cargo.route_specification.arrival_deadline.date().isoformat()
           if request.method == 'POST':
               deadline_value = request.POST.get('deadline', '')
  ```
