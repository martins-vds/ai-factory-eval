# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `6348f858891024d9bfc2ae05d30336a1bf9f2a12`): score 0.925, threshold 0.8, killed 49, survived 4. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:50 Mutant #17`

  ```diff
  @@ -47,7 +47,7 @@
           context = {
               'cargo': cargo,
               'destinations': destinations,
  -            'selected_destination': selected_destination,
  +            'XXselected_destinationXX': selected_destination,
           }
           if request.method == 'POST':
               if selected_destination is None:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:88 Mutant #38`

  ```diff
  @@ -85,7 +85,7 @@
               return _not_found(request, tracking_id)
           if request.method == 'POST':
  -            deadline_value = request.POST.get('arrival_deadline', '')
  +            deadline_value = request.POST.get('arrival_deadline', 'XXXX')
               try:
                   arrival_date = date.fromisoformat(deadline_value)
               except ValueError:
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:96 Mutant #42`

  ```diff
  @@ -93,7 +93,7 @@
                       request,
                       'booking/dialogs/deadline.html',
                       {
  -                        'cargo': cargo,
  +                        'XXcargoXX': cargo,
                           'deadline_value': deadline_value,
                           'deadline_error': 'Enter a valid arrival deadline.',
                       },
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:97 Mutant #43`

  ```diff
  @@ -94,7 +94,7 @@
                       'booking/dialogs/deadline.html',
                       {
                           'cargo': cargo,
  -                        'deadline_value': deadline_value,
  +                        'XXdeadline_valueXX': deadline_value,
                           'deadline_error': 'Enter a valid arrival deadline.',
                       },
                   )
  ```

