# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `origin/main`): score 0.907, threshold 0.8, killed 49, survived 5. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:39 Mutant #12`

  ```diff
  @@ -36,7 +36,7 @@
       try:
           mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
       except (OSError, yaml.YAMLError) as error:
  -        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
  +        raise DataExportError(f'XX{mapping_file}: unable to read mapping: {error}XX') from error
       if not isinstance(mapping, dict):
           raise DataExportError(f'{mapping_file}: mapping must be an object')
  ```

- `src/cargotracker/data_migration/exporter.py:41 Mutant #14`

  ```diff
  @@ -38,7 +38,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
       if not isinstance(mapping, dict):
  -        raise DataExportError(f'{mapping_file}: mapping must be an object')
  +        raise DataExportError(f'XX{mapping_file}: mapping must be an objectXX')
       try:
           tables = _prepare_tables(mapping, _model_index())
  ```

- `src/cargotracker/data_migration/exporter.py:70 Mutant #43`

  ```diff
  @@ -67,6 +67,6 @@
                       count += 1
               exported.append((spec['target'], count))
       except OSError as error:
  -        raise DataExportError(f'{output}: unable to write export: {error}') from error
  +        raise DataExportError(f'XX{output}: unable to write export: {error}XX') from error
       return exported
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
