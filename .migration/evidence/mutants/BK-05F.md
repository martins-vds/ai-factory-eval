# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `b9e468fb6683d78aed40e0cfcfc50bc216e9812d`): score 0.667, threshold 0.8, killed 28, survived 14. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:26 Mutant #3`

  ```diff
  @@ -23,7 +23,7 @@
       ) -> HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           if request.method == 'POST':
               selected_index = candidate_index
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:29 Mutant #6`

  ```diff
  @@ -26,7 +26,7 @@
               raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
           if request.method == 'POST':
  -            selected_index = candidate_index
  +            selected_index = None
               if selected_index is None:
                   selected_index = (
                       request.POST.get('candidate_index')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:30 Mutant #7`

  ```diff
  @@ -27,7 +27,7 @@
           if request.method == 'POST':
               selected_index = candidate_index
  -            if selected_index is None:
  +            if selected_index is not None:
                   selected_index = (
                       request.POST.get('candidate_index')
                       or request.POST.get('routeIndex')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:32 Mutant #8`

  ```diff
  @@ -29,7 +29,7 @@
               selected_index = candidate_index
               if selected_index is None:
                   selected_index = (
  -                    request.POST.get('candidate_index')
  +                    request.POST.get('XXcandidate_indexXX')
                       or request.POST.get('routeIndex')
                       or request.POST.get('itineraryIndex')
                   )
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:33 Mutant #9`

  ```diff
  @@ -30,7 +30,7 @@
               if selected_index is None:
                   selected_index = (
                       request.POST.get('candidate_index')
  -                    or request.POST.get('routeIndex')
  +                    or request.POST.get('XXrouteIndexXX')
                       or request.POST.get('itineraryIndex')
                   )
               return assign_candidate(request, tracking_id, selected_index)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:34 Mutant #10`

  ```diff
  @@ -31,7 +31,7 @@
                   selected_index = (
                       request.POST.get('candidate_index')
                       or request.POST.get('routeIndex')
  -                    or request.POST.get('itineraryIndex')
  +                    or request.POST.get('XXitineraryIndexXX')
                   )
               return assign_candidate(request, tracking_id, selected_index)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:34 Mutant #11`

  ```diff
  @@ -29,8 +29,7 @@
               selected_index = candidate_index
               if selected_index is None:
                   selected_index = (
  -                    request.POST.get('candidate_index')
  -                    or request.POST.get('routeIndex')
  +                    request.POST.get('candidate_index') and request.POST.get('routeIndex')
                       or request.POST.get('itineraryIndex')
                   )
               return assign_candidate(request, tracking_id, selected_index)
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:35 Mutant #12`

  ```diff
  @@ -28,11 +28,7 @@
           if request.method == 'POST':
               selected_index = candidate_index
               if selected_index is None:
  -                selected_index = (
  -                    request.POST.get('candidate_index')
  -                    or request.POST.get('routeIndex')
  -                    or request.POST.get('itineraryIndex')
  -                )
  +                selected_index = None
               return assign_candidate(request, tracking_id, selected_index)
           candidates = cargo_routing.route_candidates(TrackingId(tracking_id))
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:55 Mutant #20`

  ```diff
  @@ -52,7 +52,7 @@
       ) -> HttpResponse:
           cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           candidates = cargo_routing.route_candidates(TrackingId(tracking_id))
           return render(
               request,
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:61 Mutant #23`

  ```diff
  @@ -58,7 +58,7 @@
               request,
               'booking/route_selection/itinerary_selection.html',
               {
  -                'cargo': cargo,
  +                'XXcargoXX': cargo,
                   'candidate_count': len(candidates),
                   'candidates': candidates,
               },
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:62 Mutant #24`

  ```diff
  @@ -59,7 +59,7 @@
               'booking/route_selection/itinerary_selection.html',
               {
                   'cargo': cargo,
  -                'candidate_count': len(candidates),
  +                'XXcandidate_countXX': len(candidates),
                   'candidates': candidates,
               },
           )
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:75 Mutant #28`

  ```diff
  @@ -72,7 +72,7 @@
           if candidate_index is None:
               candidate_index = (
                   request.POST.get('candidate_index')
  -                or request.POST.get('routeIndex')
  +                or request.POST.get('XXrouteIndexXX')
                   or request.POST.get('itineraryIndex')
               )
           if candidate_index is None:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:76 Mutant #29`

  ```diff
  @@ -73,7 +73,7 @@
               candidate_index = (
                   request.POST.get('candidate_index')
                   or request.POST.get('routeIndex')
  -                or request.POST.get('itineraryIndex')
  +                or request.POST.get('XXitineraryIndexXX')
               )
           if candidate_index is None:
               raise Http404('A route candidate index is required.')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:86 Mutant #39`

  ```diff
  @@ -83,7 +83,7 @@
               raise Http404('A valid route candidate index is required.') from error
           candidates = cargo_routing.route_candidates(TrackingId(tracking_id))
  -        if index < 0 or index >= len(candidates):
  +        if index < 0 or index > len(candidates):
               raise Http404('The route candidate was not found.')
           cargo_routing.assign_route(TrackingId(tracking_id), candidates[index])
           return redirect(f'/admin/cargo/{tracking_id}/')
  ```

