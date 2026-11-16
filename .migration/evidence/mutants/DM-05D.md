# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `origin/main`): score 0.762, threshold 0.8, killed 61, survived 19. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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
   def _format_value(value):
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:33 Mutant #8`

  ```diff
  @@ -30,7 +30,7 @@
       if value is None:
           return r'\N'
       if isinstance(value, datetime.datetime):
  -        if value.tzinfo is None:
  +        if value.tzinfo is not None:
               value = value.replace(tzinfo=datetime.UTC)
           value = value.astimezone(datetime.UTC)
           return value.isoformat().replace('+00:00', 'Z')
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:34 Mutant #9`

  ```diff
  @@ -31,7 +31,7 @@
           return r'\N'
       if isinstance(value, datetime.datetime):
           if value.tzinfo is None:
  -            value = value.replace(tzinfo=datetime.UTC)
  +            value = None
           value = value.astimezone(datetime.UTC)
           return value.isoformat().replace('+00:00', 'Z')
       return str(value)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:43 Mutant #18`

  ```diff
  @@ -40,7 +40,7 @@
   def _prepare_tables(mapping, models):
       specs = mapping.get('tables')
       if not isinstance(specs, list) or not specs:
  -        raise DataExportError('mapping has no tables')
  +        raise DataExportError('XXmapping has no tablesXX')
       targets = set()
       prepared = []
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:49 Mutant #22`

  ```diff
  @@ -46,7 +46,7 @@
       prepared = []
       for spec in specs:
           if not isinstance(spec, dict):
  -            raise DataExportError('each mapped table must be an object')
  +            raise DataExportError('XXeach mapped table must be an objectXX')
           target = spec.get('target')
           if not isinstance(target, str) or target in targets:
               raise DataExportError('mapping targets must be unique table names')
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:52 Mutant #28`

  ```diff
  @@ -49,7 +49,7 @@
               raise DataExportError('each mapped table must be an object')
           target = spec.get('target')
           if not isinstance(target, str) or target in targets:
  -            raise DataExportError('mapping targets must be unique table names')
  +            raise DataExportError('XXmapping targets must be unique table namesXX')
           targets.add(target)
           model = models.get(target)
           if model is None:
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:56 Mutant #31`

  ```diff
  @@ -53,7 +53,7 @@
           targets.add(target)
           model = models.get(target)
           if model is None:
  -            raise DataExportError(f'{target}: no registered Django model for target table')
  +            raise DataExportError(f'XX{target}: no registered Django model for target tableXX')
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
               raise DataExportError(f'{target}: mapping has no columns')
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:59 Mutant #37`

  ```diff
  @@ -56,7 +56,7 @@
               raise DataExportError(f'{target}: no registered Django model for target table')
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
  -            raise DataExportError(f'{target}: mapping has no columns')
  +            raise DataExportError(f'XX{target}: mapping has no columnsXX')
           fields = [_field_for_column(model, column) for column in columns]
           if model._meta.pk not in fields:
               raise DataExportError(f'{target}: mapping must include its primary key')
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:62 Mutant #40`

  ```diff
  @@ -59,7 +59,7 @@
               raise DataExportError(f'{target}: mapping has no columns')
           fields = [_field_for_column(model, column) for column in columns]
           if model._meta.pk not in fields:
  -            raise DataExportError(f'{target}: mapping must include its primary key')
  +            raise DataExportError(f'XX{target}: mapping must include its primary keyXX')
           prepared.append((target, model, list(columns), fields))
       return prepared
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:73 Mutant #45`

  ```diff
  @@ -70,7 +70,7 @@
       rows = (
           model._base_manager.order_by(model._meta.pk.name)
           .values_list(*values)
  -        .iterator(chunk_size=1000)
  +        .iterator(chunk_size=1001)
       )
       count = 0
       try:
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:84 Mutant #56`

  ```diff
  @@ -81,7 +81,7 @@
                   writer.writerow(_format_value(value) for value in row)
                   count += 1
       except OSError as error:
  -        raise DataExportError(f'{path}: {error}') from error
  +        raise DataExportError(f'XX{path}: {error}XX') from error
       return target, count
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:93 Mutant #60`

  ```diff
  @@ -90,7 +90,7 @@
       try:
           mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8'))
       except (OSError, yaml.YAMLError) as error:
  -        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
  +        raise DataExportError(f'XX{mapping_file}: unable to read mapping: {error}XX') from error
       if mapping is None:
           mapping = {}
       if not isinstance(mapping, dict):
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:95 Mutant #62`

  ```diff
  @@ -92,7 +92,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
       if mapping is None:
  -        mapping = {}
  +        mapping = None
       if not isinstance(mapping, dict):
           raise DataExportError(f'{mapping_file}: mapping must be an object')
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:97 Mutant #64`

  ```diff
  @@ -94,7 +94,7 @@
       if mapping is None:
           mapping = {}
       if not isinstance(mapping, dict):
  -        raise DataExportError(f'{mapping_file}: mapping must be an object')
  +        raise DataExportError(f'XX{mapping_file}: mapping must be an objectXX')
       prepared = _prepare_tables(mapping, _model_index())
       output_dir = Path(output_path)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:104 Mutant #69`

  ```diff
  @@ -101,7 +101,7 @@
       try:
           output_dir.mkdir(parents=True, exist_ok=True)
       except OSError as error:
  -        raise DataExportError(f'{output_dir}: {error}') from error
  +        raise DataExportError(f'XX{output_dir}: {error}XX') from error
       return [
           _write_table(output_dir, target, model, columns, fields)
           for target, model, columns, fields in prepared
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:112 Mutant #70`

  ```diff
  @@ -109,7 +109,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as a relational snapshot.'
  +    help = 'XXExport mapped target tables as a relational snapshot.XX'
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:112 Mutant #71`

  ```diff
  @@ -109,7 +109,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as a relational snapshot.'
  +    help = None
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:125 Mutant #80`

  ```diff
  @@ -122,6 +122,6 @@
               raise CommandError(str(error)) from error
           total = sum(rows for _, rows in exported)
           self.stdout.write(
  -            self.style.SUCCESS(f'Exported {total} rows across {len(exported)} mapped tables.')
  +            self.style.SUCCESS(f'XXExported {total} rows across {len(exported)} mapped tables.XX')
           )
  ```

