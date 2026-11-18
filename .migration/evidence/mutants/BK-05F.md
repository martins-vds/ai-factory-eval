# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `origin/main`): score 0.951, threshold 0.8, killed 58, survived 3. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

- `src/cargotracker/booking/interfaces/route_selection/views.py:97 Mutant #43`

  ```diff
  @@ -94,7 +94,7 @@
       try:
           candidate = signing.loads(request.POST.get('candidate'), salt=_CANDIDATE_SALT)
           if candidate['tracking_id'] != tracking_id:
  -            raise BadSignature('Candidate belongs to another cargo.')
  +            raise BadSignature('XXCandidate belongs to another cargo.XX')
           return _deserialize_itinerary(candidate['legs'])
       except (BadSignature, KeyError, TypeError, ValueError) as error:
           raise Http404('The selected route is invalid.') from error
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:100 Mutant #45`

  ```diff
  @@ -97,7 +97,7 @@
               raise BadSignature('Candidate belongs to another cargo.')
           return _deserialize_itinerary(candidate['legs'])
       except (BadSignature, KeyError, TypeError, ValueError) as error:
  -        raise Http404('The selected route is invalid.') from error
  +        raise Http404('XXThe selected route is invalid.XX') from error
   def _serialize_itinerary(itinerary: Itinerary) -> list[dict]:
  ```

