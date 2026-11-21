# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `fc3bb05ed7ecde78b513097e7cd63a7ae0095ce3`): score 0.968, threshold 0.8, killed 30, survived 1. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:39 Mutant #18`

  ```diff
  @@ -36,7 +36,7 @@
           if request.method == 'POST':
               candidate_index = _selected_candidate_index(request)
               if candidate_index is None or candidate_index < 0 or candidate_index >= len(candidates):
  -                raise Http404(f'Route candidate {candidate_index} not found.')
  +                raise Http404(f'XXRoute candidate {candidate_index} not found.XX')
               cargo_routing.assign_route(tracking, candidates[candidate_index])
               return redirect(f'/admin/cargo/{tracking.value}/')
           return None
  ```

