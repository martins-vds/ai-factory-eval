# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `origin/main`): score 0.655, threshold 0.8, killed 36, survived 19. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:20 Mutant #3`

  ```diff
  @@ -17,7 +17,7 @@
       if value is None:
           return r'\N'
       if isinstance(value, datetime.datetime):
  -        if value.utcoffset() is None:
  +        if value.utcoffset() is not None:
               value = value.replace(tzinfo=timezone)
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:21 Mutant #4`

  ```diff
  @@ -18,7 +18,7 @@
           return r'\N'
       if isinstance(value, datetime.datetime):
           if value.utcoffset() is None:
  -            value = value.replace(tzinfo=timezone)
  +            value = None
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
           return value.isoformat()
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:35 Mutant #11`

  ```diff
  @@ -32,7 +32,7 @@
       try:
           mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
       except (OSError, yaml.YAMLError) as error:
  -        raise DataLoadError(f'{mapping_file}: unable to read mapping: {error}') from error
  +        raise DataLoadError(f'XX{mapping_file}: unable to read mapping: {error}XX') from error
       if not isinstance(mapping, dict):
           raise DataLoadError(f'{mapping_file}: mapping must be an object')
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:37 Mutant #13`

  ```diff
  @@ -34,7 +34,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataLoadError(f'{mapping_file}: unable to read mapping: {error}') from error
       if not isinstance(mapping, dict):
  -        raise DataLoadError(f'{mapping_file}: mapping must be an object')
  +        raise DataLoadError(f'XX{mapping_file}: mapping must be an objectXX')
       timezone = _mapping_timezone(mapping)
       prepared = _prepare_tables(mapping, _model_index())
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:39 Mutant #14`

  ```diff
  @@ -36,7 +36,7 @@
       if not isinstance(mapping, dict):
           raise DataLoadError(f'{mapping_file}: mapping must be an object')
  -    timezone = _mapping_timezone(mapping)
  +    timezone = None
       prepared = _prepare_tables(mapping, _model_index())
       output_directory = Path(output_path)
       try:
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:43 Mutant #17`

  ```diff
  @@ -40,7 +40,7 @@
       prepared = _prepare_tables(mapping, _model_index())
       output_directory = Path(output_path)
       try:
  -        output_directory.mkdir(parents=True, exist_ok=True)
  +        output_directory.mkdir(parents=False, exist_ok=True)
       except OSError as error:
           raise DataLoadError(
               f'{output_directory}: unable to create output directory: {error}'
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:43 Mutant #18`

  ```diff
  @@ -40,7 +40,7 @@
       prepared = _prepare_tables(mapping, _model_index())
       output_directory = Path(output_path)
       try:
  -        output_directory.mkdir(parents=True, exist_ok=True)
  +        output_directory.mkdir(parents=True, exist_ok=False)
       except OSError as error:
           raise DataLoadError(
               f'{output_directory}: unable to create output directory: {error}'
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:46 Mutant #19`

  ```diff
  @@ -43,7 +43,7 @@
           output_directory.mkdir(parents=True, exist_ok=True)
       except OSError as error:
           raise DataLoadError(
  -            f'{output_directory}: unable to create output directory: {error}'
  +            f'XX{output_directory}: unable to create output directory: {error}XX'
           ) from error
       exported = []
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:62 Mutant #39`

  ```diff
  @@ -59,7 +59,7 @@
                   writer = csv.writer(stream)
                   writer.writerow([column for column, _, _ in columns])
                   rows = model._base_manager.order_by(model._meta.pk.name).values_list(*field_names)
  -                count = 0
  +                count = 1
                   for row in rows:
                       writer.writerow(_format_value(value, timezone) for value in row)
                       count += 1
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:65 Mutant #41`

  ```diff
  @@ -62,7 +62,7 @@
                   count = 0
                   for row in rows:
                       writer.writerow(_format_value(value, timezone) for value in row)
  -                    count += 1
  +                    count = 1
           except OSError as error:
               raise DataLoadError(f'{output_file}: unable to write export: {error}') from error
           exported.append((target, count))
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:65 Mutant #42`

  ```diff
  @@ -62,7 +62,7 @@
                   count = 0
                   for row in rows:
                       writer.writerow(_format_value(value, timezone) for value in row)
  -                    count += 1
  +                    count -= 1
           except OSError as error:
               raise DataLoadError(f'{output_file}: unable to write export: {error}') from error
           exported.append((target, count))
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:65 Mutant #43`

  ```diff
  @@ -62,7 +62,7 @@
                   count = 0
                   for row in rows:
                       writer.writerow(_format_value(value, timezone) for value in row)
  -                    count += 1
  +                    count += 2
           except OSError as error:
               raise DataLoadError(f'{output_file}: unable to write export: {error}') from error
           exported.append((target, count))
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:67 Mutant #44`

  ```diff
  @@ -64,7 +64,7 @@
                       writer.writerow(_format_value(value, timezone) for value in row)
                       count += 1
           except OSError as error:
  -            raise DataLoadError(f'{output_file}: unable to write export: {error}') from error
  +            raise DataLoadError(f'XX{output_file}: unable to write export: {error}XX') from error
           exported.append((target, count))
       return exported
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:73 Mutant #45`

  ```diff
  @@ -70,7 +70,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as a relational snapshot.'
  +    help = 'XXExport mapped target tables as a relational snapshot.XX'
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:73 Mutant #46`

  ```diff
  @@ -70,7 +70,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as a relational snapshot.'
  +    help = None
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:76 Mutant #48`

  ```diff
  @@ -73,7 +73,7 @@
       help = 'Export mapped target tables as a relational snapshot.'
       def add_arguments(self, parser):
  -        parser.add_argument('--mapping', required=True)
  +        parser.add_argument('--mapping', required=False)
           parser.add_argument('--out', required=True)
       def handle(self, *args, **options):
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:77 Mutant #50`

  ```diff
  @@ -74,7 +74,7 @@
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  -        parser.add_argument('--out', required=True)
  +        parser.add_argument('--out', required=False)
       def handle(self, *args, **options):
           try:
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:84 Mutant #54`

  ```diff
  @@ -81,7 +81,7 @@
               exported = export_snapshot(options['mapping'], options['out'])
           except DataLoadError as error:
               raise CommandError(str(error)) from error
  -        total = sum(rows for _, rows in exported)
  +        total = None
           self.stdout.write(
               self.style.SUCCESS(f'Exported {total} rows across {len(exported)} mapped tables.')
           )
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:86 Mutant #55`

  ```diff
  @@ -83,6 +83,6 @@
               raise CommandError(str(error)) from error
           total = sum(rows for _, rows in exported)
           self.stdout.write(
  -            self.style.SUCCESS(f'Exported {total} rows across {len(exported)} mapped tables.')
  +            self.style.SUCCESS(f'XXExported {total} rows across {len(exported)} mapped tables.XX')
           )
  ```

