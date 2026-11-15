# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `origin/main`): score 0.745, threshold 0.8, killed 38, survived 13. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:20 Mutant #6`

  ```diff
  @@ -17,7 +17,7 @@
       try:
           mapping = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
       except (OSError, yaml.YAMLError) as error:
  -        raise DataExportError(f'{path}: unable to read mapping: {error}') from error
  +        raise DataExportError(f'XX{path}: unable to read mapping: {error}XX') from error
       if not isinstance(mapping, dict):
           raise DataExportError(f'{path}: mapping must be an object')
       return mapping
  ```

- `src/cargotracker/data_migration/exporter.py:22 Mutant #8`

  ```diff
  @@ -19,7 +19,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{path}: unable to read mapping: {error}') from error
       if not isinstance(mapping, dict):
  -        raise DataExportError(f'{path}: mapping must be an object')
  +        raise DataExportError(f'XX{path}: mapping must be an objectXX')
       return mapping
  ```

- `src/cargotracker/data_migration/exporter.py:30 Mutant #10`

  ```diff
  @@ -27,7 +27,7 @@
       if value is None:
           return NULL_MARKER
       if isinstance(value, datetime.datetime):
  -        if value.tzinfo is None:
  +        if value.tzinfo is not None:
               value = value.replace(tzinfo=datetime.UTC)
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       return value
  ```

- `src/cargotracker/data_migration/exporter.py:31 Mutant #11`

  ```diff
  @@ -28,7 +28,7 @@
           return NULL_MARKER
       if isinstance(value, datetime.datetime):
           if value.tzinfo is None:
  -            value = value.replace(tzinfo=datetime.UTC)
  +            value = None
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       return value
  ```

- `src/cargotracker/data_migration/exporter.py:45 Mutant #18`

  ```diff
  @@ -42,7 +42,7 @@
           raise DataExportError(str(error)) from error
       output = Path(output_path)
  -    output.mkdir(parents=True, exist_ok=True)
  +    output.mkdir(parents=False, exist_ok=True)
       for entry in tables:
           spec = entry['spec']
           model = entry['model']
  ```

- `src/cargotracker/data_migration/exporter.py:45 Mutant #19`

  ```diff
  @@ -42,7 +42,7 @@
           raise DataExportError(str(error)) from error
       output = Path(output_path)
  -    output.mkdir(parents=True, exist_ok=True)
  +    output.mkdir(parents=True, exist_ok=False)
       for entry in tables:
           spec = entry['spec']
           model = entry['model']
  ```

- `src/cargotracker/data_migration/exporter.py:60 Mutant #39`

  ```diff
  @@ -57,7 +57,7 @@
                   writer.writerow([target_column for target_column, _, _ in columns])
                   rows = model._base_manager.order_by(primary_key.name).values_list(*values)
                   writer.writerows(
  -                    [_serialize(value) for value in row] for row in rows.iterator(chunk_size=1000)
  +                    [_serialize(value) for value in row] for row in rows.iterator(chunk_size=1001)
                   )
           except OSError as error:
               raise DataExportError(f'{path}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:63 Mutant #40`

  ```diff
  @@ -60,7 +60,7 @@
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

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:10 Mutant #4`

  ```diff
  @@ -7,7 +7,7 @@
       help = 'Export mapped target tables as snapshot-format CSV files.'
       def add_arguments(self, parser):
  -        parser.add_argument('--mapping', required=True)
  +        parser.add_argument('--mapping', required=False)
           parser.add_argument('--out', required=True)
       def handle(self, *args, **options):
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:11 Mutant #6`

  ```diff
  @@ -8,7 +8,7 @@
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  -        parser.add_argument('--out', required=True)
  +        parser.add_argument('--out', required=False)
       def handle(self, *args, **options):
           try:
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

