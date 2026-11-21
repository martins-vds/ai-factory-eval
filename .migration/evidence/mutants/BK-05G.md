# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `b773736ccfce81b6efe150bd40331263565175d5`): score 0.961, threshold 0.8, killed 49, survived 2. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:104 Mutant #29`

  ```diff
  @@ -101,7 +101,7 @@
                   request,
                   cargo,
                   locations,
  -                'Select a valid destination.',
  +                'XXSelect a valid destination.XX',
               )
           cargo_specification.change_destination(cargo.tracking_id, destination)
  ```

- `src/cargotracker/booking/interfaces/dialogs/views.py:134 Mutant #47`

  ```diff
  @@ -131,7 +131,7 @@
                   request,
                   cargo,
                   deadline_value,
  -                'Enter a valid arrival deadline.',
  +                'XXEnter a valid arrival deadline.XX',
               )
           arrival_deadline = timezone.make_aware(datetime.combine(deadline, time.min))
  ```

