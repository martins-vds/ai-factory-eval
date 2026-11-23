# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `f415794e3aff44382d65a23c7841c416c0678532`): score 0.965, threshold 0.8, killed 83, survived 3. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:34 Mutant #17`

  ```diff
  @@ -31,7 +31,7 @@
       return {
           model._meta.db_table: model
           for model in apps.get_models()
  -        if not model._meta.proxy and not model._meta.auto_created
  +        if not model._meta.proxy or not model._meta.auto_created
       }
  ```

- `src/cargotracker/data_migration/exporter.py:78 Mutant #53`

  ```diff
  @@ -75,7 +75,7 @@
       if value is None:
           return r'\N'
       if isinstance(value, datetime):
  -        if value.utcoffset() is None:
  +        if value.utcoffset() is not None:
               value = value.replace(tzinfo=UTC)
           return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, date):
  ```

- `src/cargotracker/data_migration/exporter.py:79 Mutant #54`

  ```diff
  @@ -76,7 +76,7 @@
           return r'\N'
       if isinstance(value, datetime):
           if value.utcoffset() is None:
  -            value = value.replace(tzinfo=UTC)
  +            value = None
           return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, date):
           return value.isoformat()
  ```

