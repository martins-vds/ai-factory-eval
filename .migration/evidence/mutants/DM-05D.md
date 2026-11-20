# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `bbd42f104df4a113ac65034b433328055fd8295b`): score 0.803, threshold 0.8, killed 61, survived 15. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:20 Mutant #7`

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

- `src/cargotracker/data_migration/exporter.py:22 Mutant #9`

  ```diff
  @@ -19,7 +19,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{path}: unable to read mapping: {error}') from error
       if not isinstance(mapping, dict):
  -        raise DataExportError(f'{path}: mapping must be an object')
  +        raise DataExportError(f'XX{path}: mapping must be an objectXX')
       return mapping
  ```

- `src/cargotracker/data_migration/exporter.py:30 Mutant #12`

  ```diff
  @@ -27,7 +27,7 @@
       return {
           model._meta.db_table: model
           for model in apps.get_models()
  -        if not model._meta.proxy and not model._meta.auto_created
  +        if not model._meta.proxy or not model._meta.auto_created
       }
  ```

- `src/cargotracker/data_migration/exporter.py:38 Mutant #14`

  ```diff
  @@ -35,7 +35,7 @@
       for field in model._meta.concrete_fields:
           if column in (field.column, field.name, field.attname):
               return field
  -    raise DataExportError(f'{model._meta.db_table}: no target column {column!r}')
  +    raise DataExportError(f'XX{model._meta.db_table}: no target column {column!r}XX')
   def _prepare_tables(mapping, models):
  ```

- `src/cargotracker/data_migration/exporter.py:44 Mutant #20`

  ```diff
  @@ -41,7 +41,7 @@
   def _prepare_tables(mapping, models):
       specs = mapping.get('tables')
       if not isinstance(specs, list) or not specs:
  -        raise DataExportError('mapping has no tables')
  +        raise DataExportError('XXmapping has no tablesXX')
       targets = [spec.get('target') if isinstance(spec, dict) else None for spec in specs]
       if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
           raise DataExportError('mapping targets must be unique table names')
  ```

- `src/cargotracker/data_migration/exporter.py:47 Mutant #26`

  ```diff
  @@ -44,7 +44,7 @@
           raise DataExportError('mapping has no tables')
       targets = [spec.get('target') if isinstance(spec, dict) else None for spec in specs]
       if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
  -        raise DataExportError('mapping targets must be unique table names')
  +        raise DataExportError('XXmapping targets must be unique table namesXX')
       prepared = []
       for target, spec in zip(targets, specs):
  ```

- `src/cargotracker/data_migration/exporter.py:53 Mutant #30`

  ```diff
  @@ -50,7 +50,7 @@
       for target, spec in zip(targets, specs):
           model = models.get(target)
           if model is None:
  -            raise DataExportError(f'{target}: no registered Django model for target table')
  +            raise DataExportError(f'XX{target}: no registered Django model for target tableXX')
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
               raise DataExportError(f'{target}: mapping has no columns')
  ```

- `src/cargotracker/data_migration/exporter.py:55 Mutant #35`

  ```diff
  @@ -52,7 +52,7 @@
           if model is None:
               raise DataExportError(f'{target}: no registered Django model for target table')
           columns = spec.get('columns')
  -        if not isinstance(columns, dict) or not columns:
  +        if not isinstance(columns, dict) and not columns:
               raise DataExportError(f'{target}: mapping has no columns')
           fields = [_field_for_column(model, column) for column in columns]
           if model._meta.pk not in fields:
  ```

- `src/cargotracker/data_migration/exporter.py:56 Mutant #36`

  ```diff
  @@ -53,7 +53,7 @@
               raise DataExportError(f'{target}: no registered Django model for target table')
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
  -            raise DataExportError(f'{target}: mapping has no columns')
  +            raise DataExportError(f'XX{target}: mapping has no columnsXX')
           fields = [_field_for_column(model, column) for column in columns]
           if model._meta.pk not in fields:
               raise DataExportError(f'{target}: mapping must include its primary key')
  ```

- `src/cargotracker/data_migration/exporter.py:59 Mutant #39`

  ```diff
  @@ -56,7 +56,7 @@
               raise DataExportError(f'{target}: mapping has no columns')
           fields = [_field_for_column(model, column) for column in columns]
           if model._meta.pk not in fields:
  -            raise DataExportError(f'{target}: mapping must include its primary key')
  +            raise DataExportError(f'XX{target}: mapping must include its primary keyXX')
           prepared.append((target, model, list(columns), fields))
       return prepared
  ```

- `src/cargotracker/data_migration/exporter.py:70 Mutant #41`

  ```diff
  @@ -67,7 +67,7 @@
       if isinstance(value, bool):
           return str(value).lower()
       if isinstance(value, datetime.datetime):
  -        if value.utcoffset() is None:
  +        if value.utcoffset() is not None:
               value = value.replace(tzinfo=datetime.UTC)
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, datetime.date):
  ```

- `src/cargotracker/data_migration/exporter.py:85 Mutant #50`

  ```diff
  @@ -82,7 +82,7 @@
       try:
           output.mkdir(parents=True, exist_ok=True)
       except OSError as error:
  -        raise DataExportError(f'{output}: unable to create output directory: {error}') from error
  +        raise DataExportError(f'XX{output}: unable to create output directory: {error}XX') from error
       row_counts = []
       for target, model, columns, fields in tables:
  ```

- `src/cargotracker/data_migration/exporter.py:102 Mutant #65`

  ```diff
  @@ -99,7 +99,7 @@
                       writer.writerow([_format_value(value) for value in row])
                       count += 1
           except OSError as error:
  -            raise DataExportError(f'{path}: unable to write target export: {error}') from error
  +            raise DataExportError(f'XX{path}: unable to write target export: {error}XX') from error
           row_counts.append((target, count))
       return row_counts
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

