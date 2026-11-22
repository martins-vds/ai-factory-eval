# Surviving mutants: REF-01

Written by `afs-mutation` on its last run (base `2746285675ca82e6844a0f7af25821723cccea9d`): score 0.978, threshold 0.8, killed 90, survived 2. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:45 Mutant #40`

  ```diff
  @@ -42,7 +42,7 @@
                   'model': model,
                   'columns': list(columns),
                   'fields': fields,
  -                'key_fields': key_fields,
  +                'XXkey_fieldsXX': key_fields,
               }
           )
       return prepared
  ```

- `src/cargotracker/data_migration/exporter.py:59 Mutant #53`

  ```diff
  @@ -56,7 +56,7 @@
           with path.open('w', newline='', encoding='utf-8') as stream:
               writer = csv.writer(stream)
               writer.writerow(table['columns'])
  -            rows = model._base_manager.order_by(*ordering).iterator(chunk_size=1000)
  +            rows = model._base_manager.order_by(*ordering).iterator(chunk_size=1001)
               writer.writerows(
                   [
                       format_value(getattr(row, table['fields'][column].attname), timezone)
  ```

