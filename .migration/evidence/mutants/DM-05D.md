# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `origin/main`): score 0.836, threshold 0.8, killed 46, survived 9. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

