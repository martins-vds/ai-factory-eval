# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.967, threshold 0.8, killed 58, survived 2. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:63 Mutant #33`

  ```diff
  @@ -60,7 +60,7 @@
                       {
                           'cargo': cargo,
                           'locations': locations,
  -                        'destination_error': 'Select an available destination.',
  +                        'destination_error': 'XXSelect an available destination.XX',
                       },
                   )
               specification.change_destination(cargo.tracking_id, destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:102 Mutant #58`

  ```diff
  @@ -99,7 +99,7 @@
               try:
                   arrival_deadline = datetime.strptime(deadline_value, '%Y-%m-%d').date()
               except ValueError:
  -                context['deadline_error'] = 'Enter a valid arrival deadline.'
  +                context['deadline_error'] = 'XXEnter a valid arrival deadline.XX'
               else:
                   specification.change_deadline(
                       cargo.tracking_id,
  ```

