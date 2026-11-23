# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `af7b0f50a4466466d767a8b3fe238a5cb3c2ef8f`): score 0.679, threshold 0.8, killed 36, survived 17. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:22 Mutant #3`

  ```diff
  @@ -19,7 +19,7 @@
       if value is None:
           return r'\N'
       if isinstance(value, datetime.datetime):
  -        if value.utcoffset() is None:
  +        if value.utcoffset() is not None:
               value = value.replace(tzinfo=datetime.UTC)
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
  ```

- `src/cargotracker/data_migration/exporter.py:23 Mutant #4`

  ```diff
  @@ -20,7 +20,7 @@
           return r'\N'
       if isinstance(value, datetime.datetime):
           if value.utcoffset() is None:
  -            value = value.replace(tzinfo=datetime.UTC)
  +            value = None
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
           return value.isoformat()
  ```

- `src/cargotracker/data_migration/exporter.py:36 Mutant #12`

  ```diff
  @@ -33,7 +33,7 @@
       try:
           mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
       except (OSError, yaml.YAMLError) as error:
  -        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
  +        raise DataExportError(f'XX{mapping_file}: unable to read mapping: {error}XX') from error
       if not isinstance(mapping, dict):
           raise DataExportError(f'{mapping_file}: mapping must be an object')
  ```

- `src/cargotracker/data_migration/exporter.py:38 Mutant #14`

  ```diff
  @@ -35,7 +35,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
       if not isinstance(mapping, dict):
  -        raise DataExportError(f'{mapping_file}: mapping must be an object')
  +        raise DataExportError(f'XX{mapping_file}: mapping must be an objectXX')
       try:
           tables = _prepare_tables(mapping, _model_index())
  ```

- `src/cargotracker/data_migration/exporter.py:46 Mutant #16`

  ```diff
  @@ -43,7 +43,7 @@
           raise DataExportError(str(error)) from error
       try:
  -        output.mkdir(parents=True, exist_ok=True)
  +        output.mkdir(parents=False, exist_ok=True)
           row_counts = []
           for table in tables:
               target = table['spec']['target']
  ```

- `src/cargotracker/data_migration/exporter.py:46 Mutant #17`

  ```diff
  @@ -43,7 +43,7 @@
           raise DataExportError(str(error)) from error
       try:
  -        output.mkdir(parents=True, exist_ok=True)
  +        output.mkdir(parents=True, exist_ok=False)
           row_counts = []
           for table in tables:
               target = table['spec']['target']
  ```

- `src/cargotracker/data_migration/exporter.py:61 Mutant #37`

  ```diff
  @@ -58,7 +58,7 @@
               with path.open('w', encoding='utf-8', newline='') as stream:
                   writer = csv.writer(stream, lineterminator='\n')
                   writer.writerow(columns)
  -                row_count = 0
  +                row_count = 1
                   for row in rows:
                       writer.writerow([_serialize(value) for value in row])
                       row_count += 1
  ```

- `src/cargotracker/data_migration/exporter.py:64 Mutant #39`

  ```diff
  @@ -61,7 +61,7 @@
                   row_count = 0
                   for row in rows:
                       writer.writerow([_serialize(value) for value in row])
  -                    row_count += 1
  +                    row_count = 1
               row_counts.append((target, row_count))
       except OSError as error:
           raise DataExportError(f'{output}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:64 Mutant #40`

  ```diff
  @@ -61,7 +61,7 @@
                   row_count = 0
                   for row in rows:
                       writer.writerow([_serialize(value) for value in row])
  -                    row_count += 1
  +                    row_count -= 1
               row_counts.append((target, row_count))
       except OSError as error:
           raise DataExportError(f'{output}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:64 Mutant #41`

  ```diff
  @@ -61,7 +61,7 @@
                   row_count = 0
                   for row in rows:
                       writer.writerow([_serialize(value) for value in row])
  -                    row_count += 1
  +                    row_count += 2
               row_counts.append((target, row_count))
       except OSError as error:
           raise DataExportError(f'{output}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:67 Mutant #42`

  ```diff
  @@ -64,6 +64,6 @@
                       row_count += 1
               row_counts.append((target, row_count))
       except OSError as error:
  -        raise DataExportError(f'{output}: unable to write export: {error}') from error
  +        raise DataExportError(f'XX{output}: unable to write export: {error}XX') from error
       return row_counts
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:7 Mutant #1`

  ```diff
  @@ -4,7 +4,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as a relational snapshot.'
  +    help = 'XXExport mapped target tables as a relational snapshot.XX'
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:7 Mutant #2`

  ```diff
  @@ -4,7 +4,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as a relational snapshot.'
  +    help = None
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:10 Mutant #4`

  ```diff
  @@ -7,7 +7,7 @@
       help = 'Export mapped target tables as a relational snapshot.'
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

