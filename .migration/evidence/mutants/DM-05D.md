# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `origin/main`): score 0.849, threshold 0.8, killed 45, survived 8. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

