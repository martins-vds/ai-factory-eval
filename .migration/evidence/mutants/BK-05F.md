# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `origin/main`): score 0.898, threshold 0.8, killed 44, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:19 Mutant #1`

  ```diff
  @@ -16,7 +16,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_TOKEN_SALT = 'booking.route-selection.candidate'
  +_CANDIDATE_TOKEN_SALT = 'XXbooking.route-selection.candidateXX'
   def _candidate_token(tracking_id: TrackingId, itinerary: Itinerary) -> str:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:19 Mutant #2`

  ```diff
  @@ -16,7 +16,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_TOKEN_SALT = 'booking.route-selection.candidate'
  +_CANDIDATE_TOKEN_SALT = None
   def _candidate_token(tracking_id: TrackingId, itinerary: Itinerary) -> str:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:53 Mutant #19`

  ```diff
  @@ -50,7 +50,7 @@
   ) -> Itinerary:
       payload = signing.loads(token, salt=_CANDIDATE_TOKEN_SALT)
       if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id.value:
  -        raise signing.BadSignature('Candidate does not match cargo')
  +        raise signing.BadSignature('XXCandidate does not match cargoXX')
       try:
           legs = [
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:74 Mutant #33`

  ```diff
  @@ -71,7 +71,7 @@
           ]
           return Itinerary(legs)
       except (KeyError, TypeError, ValueError) as error:
  -        raise signing.BadSignature('Invalid candidate itinerary') from error
  +        raise signing.BadSignature('XXInvalid candidate itineraryXX') from error
   def create_route_selection_view(
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:85 Mutant #37`

  ```diff
  @@ -82,7 +82,7 @@
           cargo_tracking_id = TrackingId(tracking_id)
           cargo = cargo_dashboard.get_cargo_details(cargo_tracking_id)
           if cargo is None:
  -            raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +            raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
           if request.method == 'POST':
               try:
  ```

