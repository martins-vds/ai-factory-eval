# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `origin/main`): score 0.850, threshold 0.8, killed 51, survived 9. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

- `src/cargotracker/booking/interfaces/route_selection/views.py:34 Mutant #10`

  ```diff
  @@ -31,7 +31,7 @@
           if request.method == 'POST':
               cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
               if cargo is None:
  -                raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +                raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
               itinerary = _selected_itinerary(request, tracking_id)
               if not cargo.route_specification.is_satisfied_by(itinerary):
                   raise Http404('The selected route no longer satisfies the route specification.')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:37 Mutant #13`

  ```diff
  @@ -34,7 +34,7 @@
                   raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
               itinerary = _selected_itinerary(request, tracking_id)
               if not cargo.route_specification.is_satisfied_by(itinerary):
  -                raise Http404('The selected route no longer satisfies the route specification.')
  +                raise Http404('XXThe selected route no longer satisfies the route specification.XX')
               cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
               return redirect(f'/admin/cargo/{quote(tracking_id, safe="")}/')
           context = _selection_context(
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

- `src/cargotracker/booking/interfaces/route_selection/views.py:44 Mutant #16`

  ```diff
  @@ -41,7 +41,7 @@
               cargo_routing,
               cargo_dashboard,
               tracking_id,
  -            'Try setting an arrival deadline further into the future.',
  +            'XXTry setting an arrival deadline further into the future.XX',
           )
           return render(request, 'booking/route_selection/route.html', context)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:54 Mutant #21`

  ```diff
  @@ -51,7 +51,7 @@
               cargo_routing,
               cargo_dashboard,
               tracking_id,
  -            'Try setting the arrival deadline further into the future (a few weeks at least).',
  +            'XXTry setting the arrival deadline further into the future (a few weeks at least).XX',
           )
           return render(request, 'booking/route_selection/select_itinerary.html', context)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:70 Mutant #27`

  ```diff
  @@ -67,7 +67,7 @@
       tracking_id = TrackingId(tracking_id_value)
       cargo = cargo_dashboard.get_cargo_details(tracking_id)
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       itineraries = cargo_routing.route_candidates(tracking_id)
       return {
           'cargo': cargo,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:100 Mutant #44`

  ```diff
  @@ -97,7 +97,7 @@
               raise BadSignature
           return _deserialize_itinerary(candidate['legs'])
       except (BadSignature, KeyError, TypeError, ValueError) as error:
  -        raise Http404('The selected route is invalid.') from error
  +        raise Http404('XXThe selected route is invalid.XX') from error
   def _serialize_itinerary(itinerary: Itinerary) -> list[dict]:
  ```

