# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `origin/main`): score 0.827, threshold 0.8, killed 43, survived 9. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:20 Mutant #5`

  ```diff
  @@ -17,7 +17,7 @@
       try:
           mapping = yaml.safe_load(path.read_text(encoding='utf-8'))
       except (OSError, yaml.YAMLError) as error:
  -        raise DataExportError(f'{path}: unable to read mapping: {error}') from error
  +        raise DataExportError(f'XX{path}: unable to read mapping: {error}XX') from error
       if mapping is None:
           mapping = {}
       if not isinstance(mapping, dict):
  ```

- `src/cargotracker/data_migration/exporter.py:22 Mutant #7`

  ```diff
  @@ -19,7 +19,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{path}: unable to read mapping: {error}') from error
       if mapping is None:
  -        mapping = {}
  +        mapping = None
       if not isinstance(mapping, dict):
           raise DataExportError(f'{path}: mapping must be an object')
       return mapping
  ```

- `src/cargotracker/data_migration/exporter.py:32 Mutant #11`

  ```diff
  @@ -29,7 +29,7 @@
       if value is None:
           return NULL_MARKER
       if isinstance(value, datetime.datetime):
  -        if value.tzinfo is None:
  +        if value.tzinfo is not None:
               value = value.replace(tzinfo=datetime.UTC)
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       return value
  ```

- `src/cargotracker/data_migration/exporter.py:33 Mutant #12`

  ```diff
  @@ -30,7 +30,7 @@
           return NULL_MARKER
       if isinstance(value, datetime.datetime):
           if value.tzinfo is None:
  -            value = value.replace(tzinfo=datetime.UTC)
  +            value = None
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       return value
  ```

- `src/cargotracker/data_migration/exporter.py:62 Mutant #40`

  ```diff
  @@ -59,7 +59,7 @@
                   writer.writerow([target_column for target_column, _, _ in columns])
                   rows = model._base_manager.order_by(primary_key.name).values_list(*values)
                   writer.writerows(
  -                    [_serialize(value) for value in row] for row in rows.iterator(chunk_size=1000)
  +                    [_serialize(value) for value in row] for row in rows.iterator(chunk_size=1001)
                   )
           except OSError as error:
               raise DataExportError(f'{path}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:65 Mutant #41`

  ```diff
  @@ -62,7 +62,7 @@
                       [_serialize(value) for value in row] for row in rows.iterator(chunk_size=1000)
                   )
           except OSError as error:
  -            raise DataExportError(f'{path}: unable to write export: {error}') from error
  +            raise DataExportError(f'XX{path}: unable to write export: {error}XX') from error
       return len(tables)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:7 Mutant #1`

  ```diff
  @@ -4,7 +4,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as snapshot-format CSV files.'
  +    help = 'XXExport mapped target tables as snapshot-format CSV files.XX'
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:7 Mutant #2`

  ```diff
  @@ -4,7 +4,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as snapshot-format CSV files.'
  +    help = None
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:19 Mutant #11`

  ```diff
  @@ -16,6 +16,6 @@
           except DataExportError as error:
               raise CommandError(str(error)) from error
           self.stdout.write(
  -            self.style.SUCCESS(f'Exported {tables} mapped tables to {options["out"]}.')
  +            self.style.SUCCESS(f'XXExported {tables} mapped tables to {options["out"]}.XX')
           )
  ```

