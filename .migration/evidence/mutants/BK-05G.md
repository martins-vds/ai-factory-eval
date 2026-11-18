# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.935, threshold 0.8, killed 58, survived 4. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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
