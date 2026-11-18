# Surviving mutants: BK-05G

Written by `afs-mutation` on its last run (base `origin/main`): score 0.981, threshold 0.8, killed 52, survived 1. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/dialogs/views.py:46 Mutant #22`

  ```diff
  @@ -43,7 +43,7 @@
           ]
           destination_error = ''
           if request.method == 'POST':
  -            destination_code = request.POST.get('destination', '')
  +            destination_code = request.POST.get('destination', 'XXXX')
               destination = next(
                   (
                       location
  ```

