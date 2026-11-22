# Surviving mutants: REF-20261122-ADMIN-LIVE-MAP

Written by `afs-mutation` on its last run (base `0eb33070a765c30ce7c99fe4c30112d1d8bba842`): score 0.973, threshold 0.8, killed 36, survived 1. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/cargo/application/admin_map.py:7 Mutant #1`

  ```diff
  @@ -4,7 +4,7 @@
   from cargotracker.cargo.application.admin_map_data import build_cargo_map_data
   from cargotracker.cargo.domain.repository import CargoRepository
  -UNKNOWN_LOCATION = admin_map_data.UNKNOWN_LOCATION
  +UNKNOWN_LOCATION = None
   def build_admin_map_data(
  ```

