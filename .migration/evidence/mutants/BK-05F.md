# Surviving mutants: BK-05F

Written by `afs-mutation` on its last run (base `6d29ae7f70131c9eb6ea6964c5eacb3650352052`): score 0.828, threshold 0.8, killed 53, survived 11. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/booking/interfaces/route_selection/views.py:26 Mutant #1`

  ```diff
  @@ -23,7 +23,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SIGNING_SALT = 'cargotracker.booking.route_selection'
  +_CANDIDATE_SIGNING_SALT = 'XXcargotracker.booking.route_selectionXX'
   def _candidate_token(tracking_id: str, itinerary: Itinerary) -> str:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:26 Mutant #2`

  ```diff
  @@ -23,7 +23,7 @@
   from cargotracker.voyage.domain.voyage import Voyage
   from cargotracker.voyage.domain.voyage_number import VoyageNumber
  -_CANDIDATE_SIGNING_SALT = 'cargotracker.booking.route_selection'
  +_CANDIDATE_SIGNING_SALT = None
   def _candidate_token(tracking_id: str, itinerary: Itinerary) -> str:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:56 Mutant #17`

  ```diff
  @@ -53,7 +53,7 @@
   ) -> Itinerary:
       payload = signing.loads(token, salt=_CANDIDATE_SIGNING_SALT)
       if not isinstance(payload, dict) or payload.get('tracking_id') != tracking_id:
  -        raise signing.BadSignature('Candidate does not belong to this cargo')
  +        raise signing.BadSignature('XXCandidate does not belong to this cargoXX')
       legs = payload.get('legs')
       if not isinstance(legs, list) or not legs:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:59 Mutant #22`

  ```diff
  @@ -56,7 +56,7 @@
           raise signing.BadSignature('Candidate does not belong to this cargo')
       legs = payload.get('legs')
  -    if not isinstance(legs, list) or not legs:
  +    if not isinstance(legs, list) and not legs:
           raise signing.BadSignature('Candidate has no itinerary legs')
       itinerary_legs = []
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:60 Mutant #23`

  ```diff
  @@ -57,7 +57,7 @@
       legs = payload.get('legs')
       if not isinstance(legs, list) or not legs:
  -        raise signing.BadSignature('Candidate has no itinerary legs')
  +        raise signing.BadSignature('XXCandidate has no itinerary legsXX')
       itinerary_legs = []
       for data in legs:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:65 Mutant #26`

  ```diff
  @@ -62,7 +62,7 @@
       itinerary_legs = []
       for data in legs:
           if not isinstance(data, dict):
  -            raise signing.BadSignature('Candidate contains an invalid itinerary leg')
  +            raise signing.BadSignature('XXCandidate contains an invalid itinerary legXX')
           try:
               voyage = Voyage(VoyageNumber(data['voyage_number']), Schedule.EMPTY)
               load_location = Location(UnLocode(data['load_unlocode']), data['load_name'])
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:73 Mutant #39`

  ```diff
  @@ -70,7 +70,7 @@
               load_time = datetime.fromisoformat(data['load_time'])
               unload_time = datetime.fromisoformat(data['unload_time'])
           except (KeyError, TypeError, ValueError) as error:
  -            raise signing.BadSignature('Candidate contains an invalid itinerary leg') from error
  +            raise signing.BadSignature('XXCandidate contains an invalid itinerary legXX') from error
           itinerary_legs.append(Leg(voyage, load_location, unload_location, load_time, unload_time))
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:117 Mutant #49`

  ```diff
  @@ -114,7 +114,7 @@
       cargo = cargo_dashboard.get_cargo_details(TrackingId(tracking_id))
       if cargo is None:
  -        raise Http404(f'Cargo with tracking ID {tracking_id} not found.')
  +        raise Http404(f'XXCargo with tracking ID {tracking_id} not found.XX')
       if request.method == 'POST':
           try:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:122 Mutant #53`

  ```diff
  @@ -119,7 +119,7 @@
       if request.method == 'POST':
           try:
               itinerary = _itinerary_from_token(
  -                request.POST.get('candidate_token', ''),
  +                request.POST.get('candidate_token', 'XXXX'),
                   tracking_id,
               )
           except signing.BadSignature:
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:126 Mutant #55`

  ```diff
  @@ -123,7 +123,7 @@
                   tracking_id,
               )
           except signing.BadSignature:
  -            return HttpResponseBadRequest('Invalid route selection.')
  +            return HttpResponseBadRequest('XXInvalid route selection.XX')
           cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
           return redirect(f'/admin/cargo/{quote(tracking_id, safe="")}/')
  ```

- `src/cargotracker/booking/interfaces/route_selection/views.py:128 Mutant #56`

  ```diff
  @@ -125,7 +125,7 @@
           except signing.BadSignature:
               return HttpResponseBadRequest('Invalid route selection.')
           cargo_routing.assign_route(TrackingId(tracking_id), itinerary)
  -        return redirect(f'/admin/cargo/{quote(tracking_id, safe="")}/')
  +        return redirect(f'/admin/cargo/{quote(tracking_id, safe="XXXX")}/')
       candidates = [
           {'itinerary': itinerary, 'token': _candidate_token(tracking_id, itinerary)}
  ```

