# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `origin/main`): score 0.950, threshold 0.8, killed 57, survived 3. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:22 Mutant #1`

  ```diff
  @@ -19,7 +19,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'booking.route_selection'
  +_CANDIDATE_SALT = 'XXbooking.route_selectionXX'
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:22 Mutant #2`

  ```diff
  @@ -19,7 +19,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SALT = 'booking.route_selection'
  +_CANDIDATE_SALT = None
   def create_route_selection_views(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:39 Mutant #14`

  ```diff
  @@ -36,7 +36,7 @@
               if not cargo.route_specification.is_satisfied_by(itinerary):
                   raise Http404('The selected route no longer satisfies the route specification.')
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
  -            return redirect(f'/admin/cargo/{quote(tracking_id, safe="")}/')
  +            return redirect(f'/admin/cargo/{quote(tracking_id, safe="XXXX")}/')
           context = _selection_context(
               cargo_routing,
               cargo_dashboard,
  ```

