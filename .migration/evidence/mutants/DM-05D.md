# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `origin/main`): score 0.660, threshold 0.8, killed 35, survived 18. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:24 Mutant #3`

  ```diff
  @@ -21,7 +21,7 @@
       if value is None:
           return '\\N'
       if isinstance(value, datetime.datetime):
  -        if value.tzinfo is None:
  +        if value.tzinfo is not None:
               value = value.replace(tzinfo=timezone)
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
  ```

- `src/cargotracker/data_migration/exporter.py:25 Mutant #4`

  ```diff
  @@ -22,7 +22,7 @@
           return '\\N'
       if isinstance(value, datetime.datetime):
           if value.tzinfo is None:
  -            value = value.replace(tzinfo=timezone)
  +            value = None
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
           return value.isoformat()
  ```

- `src/cargotracker/data_migration/exporter.py:37 Mutant #11`

  ```diff
  @@ -34,7 +34,7 @@
       try:
           mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
       except (OSError, yaml.YAMLError) as error:
  -        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
  +        raise DataExportError(f'XX{mapping_file}: unable to read mapping: {error}XX') from error
       if not isinstance(mapping, dict):
           raise DataExportError(f'{mapping_file}: mapping must be an object')
  ```

- `src/cargotracker/data_migration/exporter.py:39 Mutant #13`

  ```diff
  @@ -36,7 +36,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
       if not isinstance(mapping, dict):
  -        raise DataExportError(f'{mapping_file}: mapping must be an object')
  +        raise DataExportError(f'XX{mapping_file}: mapping must be an objectXX')
       try:
           prepared = _prepare_tables(mapping, _model_index())
  ```

- `src/cargotracker/data_migration/exporter.py:43 Mutant #15`

  ```diff
  @@ -40,7 +40,7 @@
       try:
           prepared = _prepare_tables(mapping, _model_index())
  -        timezone = _mapping_timezone(mapping)
  +        timezone = None
       except (DataLoadError, ImproperlyConfigured) as error:
           raise DataExportError(str(error)) from error
  ```

- `src/cargotracker/data_migration/exporter.py:49 Mutant #17`

  ```diff
  @@ -46,7 +46,7 @@
       output = Path(output_path)
       try:
  -        output.mkdir(parents=True, exist_ok=True)
  +        output.mkdir(parents=False, exist_ok=True)
           row_counts = []
           for entry in prepared:
               spec = entry['spec']
  ```

- `src/cargotracker/data_migration/exporter.py:49 Mutant #18`

  ```diff
  @@ -46,7 +46,7 @@
       output = Path(output_path)
       try:
  -        output.mkdir(parents=True, exist_ok=True)
  +        output.mkdir(parents=True, exist_ok=False)
           row_counts = []
           for entry in prepared:
               spec = entry['spec']
  ```

- `src/cargotracker/data_migration/exporter.py:56 Mutant #28`

  ```diff
  @@ -53,7 +53,7 @@
               model = entry['model']
               columns = entry['columns']
               field_names = [entry['fields'][name].attname for name, _, _ in columns]
  -            row_count = 0
  +            row_count = 1
               with (output / f'{spec["target"]}.csv').open(
                   'w',
                   encoding='utf-8',
  ```

- `src/cargotracker/data_migration/exporter.py:71 Mutant #38`

  ```diff
  @@ -68,7 +68,7 @@
                   )
                   for row in rows:
                       writer.writerow(_format_value(value, timezone) for value in row)
  -                    row_count += 1
  +                    row_count = 1
               row_counts.append((spec['target'], row_count))
       except OSError as error:
           raise DataExportError(f'{output}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:71 Mutant #39`

  ```diff
  @@ -68,7 +68,7 @@
                   )
                   for row in rows:
                       writer.writerow(_format_value(value, timezone) for value in row)
  -                    row_count += 1
  +                    row_count -= 1
               row_counts.append((spec['target'], row_count))
       except OSError as error:
           raise DataExportError(f'{output}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:71 Mutant #40`

  ```diff
  @@ -68,7 +68,7 @@
                   )
                   for row in rows:
                       writer.writerow(_format_value(value, timezone) for value in row)
  -                    row_count += 1
  +                    row_count += 2
               row_counts.append((spec['target'], row_count))
       except OSError as error:
           raise DataExportError(f'{output}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:74 Mutant #42`

  ```diff
  @@ -71,6 +71,6 @@
                       row_count += 1
               row_counts.append((spec['target'], row_count))
       except OSError as error:
  -        raise DataExportError(f'{output}: unable to write export: {error}') from error
  +        raise DataExportError(f'XX{output}: unable to write export: {error}XX') from error
       return row_counts
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:7 Mutant #1`

  ```diff
  @@ -4,7 +4,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as a CSV snapshot.'
  +    help = 'XXExport mapped target tables as a CSV snapshot.XX'
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:7 Mutant #2`

  ```diff
  @@ -4,7 +4,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as a CSV snapshot.'
  +    help = None
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:10 Mutant #4`

  ```diff
  @@ -7,7 +7,7 @@
       help = 'Export mapped target tables as a CSV snapshot.'
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

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:18 Mutant #10`

  ```diff
  @@ -15,7 +15,7 @@
               exported = export_snapshot(options['mapping'], options['out'])
           except DataExportError as error:
               raise CommandError(str(error)) from error
  -        total = sum(rows for _, rows in exported)
  +        total = None
           self.stdout.write(
               self.style.SUCCESS(f'Exported {total} rows across {len(exported)} mapped tables.')
           )
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:20 Mutant #11`

  ```diff
  @@ -17,6 +17,6 @@
               raise CommandError(str(error)) from error
           total = sum(rows for _, rows in exported)
           self.stdout.write(
  -            self.style.SUCCESS(f'Exported {total} rows across {len(exported)} mapped tables.')
  +            self.style.SUCCESS(f'XXExported {total} rows across {len(exported)} mapped tables.XX')
           )
  ```

