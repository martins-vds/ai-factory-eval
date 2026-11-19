# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `f588d5360f7175491af1ab3d9688571ea0fd7d2f`): score 0.949, threshold 0.8, killed 74, survived 4. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:39 Mutant #17`

  ```diff
  @@ -36,7 +36,7 @@
       models = {
           model._meta.db_table: model
           for model in apps.get_models()
  -        if not model._meta.proxy and not model._meta.auto_created
  +        if not model._meta.proxy or not model._meta.auto_created
       }
       mapped = []
       targets = set()
  ```

- `src/cargotracker/data_migration/exporter.py:68 Mutant #43`

  ```diff
  @@ -65,7 +65,7 @@
       if value is None:
           return r'\N'
       if isinstance(value, datetime.datetime):
  -        if value.tzinfo is None:
  +        if value.tzinfo is not None:
               value = value.replace(tzinfo=datetime.UTC)
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
  ```

- `src/cargotracker/data_migration/exporter.py:69 Mutant #44`

  ```diff
  @@ -66,7 +66,7 @@
           return r'\N'
       if isinstance(value, datetime.datetime):
           if value.tzinfo is None:
  -            value = value.replace(tzinfo=datetime.UTC)
  +            value = None
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
           return value.isoformat()
  ```

- `src/cargotracker/data_migration/exporter.py:94 Mutant #63`

  ```diff
  @@ -91,7 +91,7 @@
                   values = model._base_manager.order_by(model._meta.pk.attname).values_list(
                       *(field.attname for _, field in fields)
                   )
  -                for row in values.iterator(chunk_size=1000):
  +                for row in values.iterator(chunk_size=1001):
                       writer.writerow(_csv_value(value) for value in row)
                       rows_written += 1
               row_counts.append((target, rows_written))
  ```

