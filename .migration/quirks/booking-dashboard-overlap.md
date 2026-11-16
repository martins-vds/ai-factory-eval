# Booking dashboard may list claimed, unrouted cargo twice

## Question
If a claimed cargo has no itinerary, should it appear in both Not Routed Cargo and Claimed Cargo? Preserve, fix, or something else?

## Evidence
- Source: `.source/src/main/java/org/eclipse/cargotracker/interfaces/booking/web/ListCargo.java:69-88` filters claimed and not-routed cargo independently; `.source/src/main/java/org/eclipse/cargotracker/interfaces/booking/facade/dto/CargoRoute.java:92-94,108-110` defines routed by nonempty legs and claimed by an independent flag.
- Characterization: the tier-A dashboard observation covers seeded routed, not-routed, and claimed rows but does not include a claimed row with no itinerary. The source predicates imply such a row is returned by both getters.
- Why it looks wrong: a cargo can be displayed twice across tables presented as distinct dashboard states.

## Impact
- Ledger capabilities: `booking.dashboard-filters`, `booking.screen-not-routed-table`, `booking.screen-claimed-table`
- Blocks: BK-05E verification of these filters and BK-05J slice acceptance until a human decides.

## Options
1. Preserve exactly (a test pins the overlap).
2. Fix (the target makes these tables mutually exclusive and the approved divergence is recorded in the ledger).
3. Other
