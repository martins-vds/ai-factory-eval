# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `ca4f4a255d67adf64ba1c12a6ec4fb144588807b`): score 0.989, threshold 0.8, killed 94, survived 1. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:84 Mutant #58`

  ```diff
  @@ -81,7 +81,7 @@
           return NULL_MARKER
       if isinstance(value, datetime.datetime):
           if value.utcoffset() is None:
  -            value = value.replace(tzinfo=timezone)
  +            value = None
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
           return value.isoformat()
  ```

