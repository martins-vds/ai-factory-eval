# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `939fd6e0e29b7dd77ccf0c1267a6ab0d4df62998`): score 0.815, threshold 0.8, killed 75, survived 17. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:19 Mutant #5`

  ```diff
  @@ -16,7 +16,7 @@
       try:
           mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
       except (OSError, yaml.YAMLError) as error:
  -        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
  +        raise DataExportError(f'XX{mapping_file}: unable to read mapping: {error}XX') from error
       if not isinstance(mapping, dict):
           raise DataExportError(f'{mapping_file}: mapping must be an object')
       return mapping
  ```

- `src/cargotracker/data_migration/exporter.py:21 Mutant #7`

  ```diff
  @@ -18,7 +18,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
       if not isinstance(mapping, dict):
  -        raise DataExportError(f'{mapping_file}: mapping must be an object')
  +        raise DataExportError(f'XX{mapping_file}: mapping must be an objectXX')
       return mapping
  ```

- `src/cargotracker/data_migration/exporter.py:29 Mutant #10`

  ```diff
  @@ -26,7 +26,7 @@
       return {
           model._meta.db_table: model
           for model in apps.get_models()
  -        if not model._meta.proxy and not model._meta.auto_created
  +        if not model._meta.proxy or not model._meta.auto_created
       }
  ```

- `src/cargotracker/data_migration/exporter.py:37 Mutant #12`

  ```diff
  @@ -34,7 +34,7 @@
       for field in model._meta.concrete_fields:
           if column in (field.column, field.name, field.attname):
               return field
  -    raise DataExportError(f'{model._meta.db_table}: no target column {column!r}')
  +    raise DataExportError(f'XX{model._meta.db_table}: no target column {column!r}XX')
   def _prepare_tables(mapping, models):
  ```

- `src/cargotracker/data_migration/exporter.py:43 Mutant #18`

  ```diff
  @@ -40,7 +40,7 @@
   def _prepare_tables(mapping, models):
       specs = mapping.get('tables')
       if not isinstance(specs, list) or not specs:
  -        raise DataExportError('mapping has no tables')
  +        raise DataExportError('XXmapping has no tablesXX')
       targets = [spec.get('target') if isinstance(spec, dict) else None for spec in specs]
       if any(not isinstance(target, str) or not target for target in targets) or len(targets) != len(
  ```

- `src/cargotracker/data_migration/exporter.py:46 Mutant #23`

  ```diff
  @@ -43,7 +43,7 @@
           raise DataExportError('mapping has no tables')
       targets = [spec.get('target') if isinstance(spec, dict) else None for spec in specs]
  -    if any(not isinstance(target, str) or not target for target in targets) or len(targets) != len(
  +    if any(not isinstance(target, str) and not target for target in targets) or len(targets) != len(
           set(targets)
       ):
           raise DataExportError('mapping targets must be unique table names')
  ```

- `src/cargotracker/data_migration/exporter.py:49 Mutant #26`

  ```diff
  @@ -46,7 +46,7 @@
       if any(not isinstance(target, str) or not target for target in targets) or len(targets) != len(
           set(targets)
       ):
  -        raise DataExportError('mapping targets must be unique table names')
  +        raise DataExportError('XXmapping targets must be unique table namesXX')
       prepared = []
       for spec in specs:
  ```

- `src/cargotracker/data_migration/exporter.py:54 Mutant #31`

  ```diff
  @@ -51,7 +51,7 @@
       prepared = []
       for spec in specs:
           target = spec['target']
  -        if Path(target).name != target or '/' in target or '\\' in target:
  +        if Path(target).name != target or 'XX/XX' in target or '\\' in target:
               raise DataExportError(f'{target}: invalid target table name')
           model = models.get(target)
           if model is None:
  ```

- `src/cargotracker/data_migration/exporter.py:54 Mutant #35`

  ```diff
  @@ -51,7 +51,7 @@
       prepared = []
       for spec in specs:
           target = spec['target']
  -        if Path(target).name != target or '/' in target or '\\' in target:
  +        if Path(target).name != target and '/' in target or '\\' in target:
               raise DataExportError(f'{target}: invalid target table name')
           model = models.get(target)
           if model is None:
  ```

- `src/cargotracker/data_migration/exporter.py:55 Mutant #36`

  ```diff
  @@ -52,7 +52,7 @@
       for spec in specs:
           target = spec['target']
           if Path(target).name != target or '/' in target or '\\' in target:
  -            raise DataExportError(f'{target}: invalid target table name')
  +            raise DataExportError(f'XX{target}: invalid target table nameXX')
           model = models.get(target)
           if model is None:
               raise DataExportError(f'{target}: no registered Django model for target table')
  ```

- `src/cargotracker/data_migration/exporter.py:58 Mutant #39`

  ```diff
  @@ -55,7 +55,7 @@
               raise DataExportError(f'{target}: invalid target table name')
           model = models.get(target)
           if model is None:
  -            raise DataExportError(f'{target}: no registered Django model for target table')
  +            raise DataExportError(f'XX{target}: no registered Django model for target tableXX')
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
  ```

- `src/cargotracker/data_migration/exporter.py:62 Mutant #45`

  ```diff
  @@ -59,7 +59,7 @@
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
  -            raise DataExportError(f'{target}: mapping has no columns')
  +            raise DataExportError(f'XX{target}: mapping has no columnsXX')
           fields = []
           for column, definition in columns.items():
  ```

- `src/cargotracker/data_migration/exporter.py:71 Mutant #53`

  ```diff
  @@ -68,7 +68,7 @@
               else:
                   source_column = definition
               if not isinstance(column, str) or not isinstance(source_column, str):
  -                raise DataExportError(f'{target}: mapping must name target and source columns')
  +                raise DataExportError(f'XX{target}: mapping must name target and source columnsXX')
               fields.append((column, _field_for_column(model, column)))
           prepared.append((target, model, fields))
  ```

- `src/cargotracker/data_migration/exporter.py:82 Mutant #56`

  ```diff
  @@ -79,7 +79,7 @@
       if value is None:
           return r'\N'
       if isinstance(value, datetime.datetime):
  -        if value.utcoffset() is None:
  +        if value.utcoffset() is not None:
               value = value.replace(tzinfo=datetime.UTC)
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
  ```

- `src/cargotracker/data_migration/exporter.py:83 Mutant #57`

  ```diff
  @@ -80,7 +80,7 @@
           return r'\N'
       if isinstance(value, datetime.datetime):
           if value.utcoffset() is None:
  -            value = value.replace(tzinfo=datetime.UTC)
  +            value = None
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
           return value.isoformat()
  ```

- `src/cargotracker/data_migration/exporter.py:114 Mutant #81`

  ```diff
  @@ -111,6 +111,6 @@
                       row_count += 1
               exported.append((target, row_count))
       except OSError as error:
  -        raise DataExportError(f'{output}: unable to write export: {error}') from error
  +        raise DataExportError(f'XX{output}: unable to write export: {error}XX') from error
       return exported
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:7 Mutant #1`

  ```diff
  @@ -4,7 +4,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as CSV files.'
  +    help = 'XXExport mapped target tables as CSV files.XX'
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

