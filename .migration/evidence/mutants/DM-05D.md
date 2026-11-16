# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `origin/main`): score 0.813, threshold 0.8, killed 61, survived 14. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:18 Mutant #3`

  ```diff
  @@ -15,7 +15,7 @@
       return {
           model._meta.db_table: model
           for model in apps.get_models()
  -        if not model._meta.proxy and not model._meta.auto_created
  +        if not model._meta.proxy or not model._meta.auto_created
       }
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:26 Mutant #5`

  ```diff
  @@ -23,7 +23,7 @@
       for field in model._meta.concrete_fields:
           if column in (field.column, field.name, field.attname):
               return field
  -    raise DataExportError(f'{model._meta.db_table}: no target column {column!r}')
  +    raise DataExportError(f'XX{model._meta.db_table}: no target column {column!r}XX')
   def _prepare_tables(mapping, models):
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:32 Mutant #11`

  ```diff
  @@ -29,7 +29,7 @@
   def _prepare_tables(mapping, models):
       specs = mapping.get('tables')
       if not isinstance(specs, list) or not specs:
  -        raise DataExportError('mapping has no tables')
  +        raise DataExportError('XXmapping has no tablesXX')
       targets = [spec.get('target') if isinstance(spec, dict) else None for spec in specs]
       if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:36 Mutant #17`

  ```diff
  @@ -33,7 +33,7 @@
       targets = [spec.get('target') if isinstance(spec, dict) else None for spec in specs]
       if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
  -        raise DataExportError('mapping targets must be unique table names')
  +        raise DataExportError('XXmapping targets must be unique table namesXX')
       prepared = []
       for spec in specs:
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:43 Mutant #23`

  ```diff
  @@ -40,7 +40,7 @@
           target = spec['target']
           model = models.get(target)
           if model is None:
  -            raise DataExportError(f'{target}: no registered Django model for target table')
  +            raise DataExportError(f'XX{target}: no registered Django model for target tableXX')
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:47 Mutant #29`

  ```diff
  @@ -44,7 +44,7 @@
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
  -            raise DataExportError(f'{target}: mapping has no columns')
  +            raise DataExportError(f'XX{target}: mapping has no columnsXX')
           fields = [(column, _field_for_column(model, column)) for column in columns]
           if model._meta.pk not in (field for _, field in fields):
               raise DataExportError(f'{target}: mapping must include its primary key')
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:50 Mutant #32`

  ```diff
  @@ -47,7 +47,7 @@
               raise DataExportError(f'{target}: mapping has no columns')
           fields = [(column, _field_for_column(model, column)) for column in columns]
           if model._meta.pk not in (field for _, field in fields):
  -            raise DataExportError(f'{target}: mapping must include its primary key')
  +            raise DataExportError(f'XX{target}: mapping must include its primary keyXX')
           prepared.append((target, model, fields))
       return prepared
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:72 Mutant #40`

  ```diff
  @@ -69,7 +69,7 @@
       try:
           mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8'))
       except (OSError, yaml.YAMLError) as error:
  -        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
  +        raise DataExportError(f'XX{mapping_file}: unable to read mapping: {error}XX') from error
       if mapping is None:
           mapping = {}
       if not isinstance(mapping, dict):
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:74 Mutant #42`

  ```diff
  @@ -71,7 +71,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
       if mapping is None:
  -        mapping = {}
  +        mapping = None
       if not isinstance(mapping, dict):
           raise DataExportError(f'{mapping_file}: mapping must be an object')
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:76 Mutant #44`

  ```diff
  @@ -73,7 +73,7 @@
       if mapping is None:
           mapping = {}
       if not isinstance(mapping, dict):
  -        raise DataExportError(f'{mapping_file}: mapping must be an object')
  +        raise DataExportError(f'XX{mapping_file}: mapping must be an objectXX')
       prepared = _prepare_tables(mapping, _model_index())
       output = Path(output_path)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:92 Mutant #60`

  ```diff
  @@ -89,7 +89,7 @@
                       *(field.attname for _, field in fields)
                   )
                   count = 0
  -                for row in rows.iterator(chunk_size=2000):
  +                for row in rows.iterator(chunk_size=2001):
                       writer.writerow([_format_value(value) for value in row])
                       count += 1
               row_counts.append((target, count))
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:97 Mutant #64`

  ```diff
  @@ -94,7 +94,7 @@
                       count += 1
               row_counts.append((target, count))
       except OSError as error:
  -        raise DataExportError(f'{output}: unable to write target export: {error}') from error
  +        raise DataExportError(f'XX{output}: unable to write target export: {error}XX') from error
       return row_counts
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:102 Mutant #65`

  ```diff
  @@ -99,7 +99,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as snapshot-format CSV files.'
  +    help = 'XXExport mapped target tables as snapshot-format CSV files.XX'
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:102 Mutant #66`

  ```diff
  @@ -99,7 +99,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as snapshot-format CSV files.'
  +    help = None
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

