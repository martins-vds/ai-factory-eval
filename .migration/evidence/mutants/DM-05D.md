# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `origin/main`): score 0.620, threshold 0.8, killed 49, survived 30. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:42 Mutant #17`

  ```diff
  @@ -39,7 +39,7 @@
   def _prepare_tables(mapping, models):
       specs = mapping.get('tables')
  -    if not isinstance(specs, list) or not specs:
  +    if not isinstance(specs, list) and not specs:
           raise DataExportError('mapping has no tables')
       targets = set()
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

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:51 Mutant #27`

  ```diff
  @@ -48,7 +48,7 @@
           if not isinstance(spec, dict):
               raise DataExportError('each mapped table must be an object')
           target = spec.get('target')
  -        if not isinstance(target, str) or target in targets:
  +        if not isinstance(target, str) and target in targets:
               raise DataExportError('mapping targets must be unique table names')
           targets.add(target)
           model = models.get(target)
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

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:58 Mutant #36`

  ```diff
  @@ -55,7 +55,7 @@
           if model is None:
               raise DataExportError(f'{target}: no registered Django model for target table')
           columns = spec.get('columns')
  -        if not isinstance(columns, dict) or not columns:
  +        if not isinstance(columns, dict) and not columns:
               raise DataExportError(f'{target}: mapping has no columns')
           fields = [_field_for_column(model, column) for column in columns]
           if model._meta.pk not in fields:
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

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:75 Mutant #47`

  ```diff
  @@ -72,7 +72,7 @@
           .values_list(*values)
           .iterator(chunk_size=1000)
       )
  -    count = 0
  +    count = 1
       try:
           with path.open('w', newline='', encoding='utf-8') as stream:
               writer = csv.writer(stream)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:82 Mutant #53`

  ```diff
  @@ -79,7 +79,7 @@
               writer.writerow(columns)
               for row in rows:
                   writer.writerow(_format_value(value) for value in row)
  -                count += 1
  +                count = 1
       except OSError as error:
           raise DataExportError(f'{path}: {error}') from error
       return target, count
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:82 Mutant #54`

  ```diff
  @@ -79,7 +79,7 @@
               writer.writerow(columns)
               for row in rows:
                   writer.writerow(_format_value(value) for value in row)
  -                count += 1
  +                count -= 1
       except OSError as error:
           raise DataExportError(f'{path}: {error}') from error
       return target, count
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:82 Mutant #55`

  ```diff
  @@ -79,7 +79,7 @@
               writer.writerow(columns)
               for row in rows:
                   writer.writerow(_format_value(value) for value in row)
  -                count += 1
  +                count += 2
       except OSError as error:
           raise DataExportError(f'{path}: {error}') from error
       return target, count
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

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:93 Mutant #61`

  ```diff
  @@ -90,7 +90,7 @@
       try:
           mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
       except (OSError, yaml.YAMLError) as error:
  -        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
  +        raise DataExportError(f'XX{mapping_file}: unable to read mapping: {error}XX') from error
       if not isinstance(mapping, dict):
           raise DataExportError(f'{mapping_file}: mapping must be an object')
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:95 Mutant #63`

  ```diff
  @@ -92,7 +92,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
       if not isinstance(mapping, dict):
  -        raise DataExportError(f'{mapping_file}: mapping must be an object')
  +        raise DataExportError(f'XX{mapping_file}: mapping must be an objectXX')
       prepared = _prepare_tables(mapping, _model_index())
       output_dir = Path(output_path)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:100 Mutant #66`

  ```diff
  @@ -97,7 +97,7 @@
       prepared = _prepare_tables(mapping, _model_index())
       output_dir = Path(output_path)
       try:
  -        output_dir.mkdir(parents=True, exist_ok=True)
  +        output_dir.mkdir(parents=False, exist_ok=True)
       except OSError as error:
           raise DataExportError(f'{output_dir}: {error}') from error
       return [
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:100 Mutant #67`

  ```diff
  @@ -97,7 +97,7 @@
       prepared = _prepare_tables(mapping, _model_index())
       output_dir = Path(output_path)
       try:
  -        output_dir.mkdir(parents=True, exist_ok=True)
  +        output_dir.mkdir(parents=True, exist_ok=False)
       except OSError as error:
           raise DataExportError(f'{output_dir}: {error}') from error
       return [
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:102 Mutant #68`

  ```diff
  @@ -99,7 +99,7 @@
       try:
           output_dir.mkdir(parents=True, exist_ok=True)
       except OSError as error:
  -        raise DataExportError(f'{output_dir}: {error}') from error
  +        raise DataExportError(f'XX{output_dir}: {error}XX') from error
       return [
           _write_table(output_dir, target, model, columns, fields)
           for target, model, columns, fields in prepared
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:110 Mutant #69`

  ```diff
  @@ -107,7 +107,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as a relational snapshot.'
  +    help = 'XXExport mapped target tables as a relational snapshot.XX'
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:110 Mutant #70`

  ```diff
  @@ -107,7 +107,7 @@
   class Command(BaseCommand):
  -    help = 'Export mapped target tables as a relational snapshot.'
  +    help = None
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:113 Mutant #72`

  ```diff
  @@ -110,7 +110,7 @@
       help = 'Export mapped target tables as a relational snapshot.'
       def add_arguments(self, parser):
  -        parser.add_argument('--mapping', required=True)
  +        parser.add_argument('--mapping', required=False)
           parser.add_argument('--out', required=True)
       def handle(self, *args, **options):
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:114 Mutant #74`

  ```diff
  @@ -111,7 +111,7 @@
       def add_arguments(self, parser):
           parser.add_argument('--mapping', required=True)
  -        parser.add_argument('--out', required=True)
  +        parser.add_argument('--out', required=False)
       def handle(self, *args, **options):
           try:
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:121 Mutant #78`

  ```diff
  @@ -118,7 +118,7 @@
               exported = export_snapshot(options['mapping'], options['out'])
           except DataExportError as error:
               raise CommandError(str(error)) from error
  -        total = sum(rows for _, rows in exported)
  +        total = None
           self.stdout.write(
               self.style.SUCCESS(f'Exported {total} rows across {len(exported)} mapped tables.')
           )
  ```

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:123 Mutant #79`

  ```diff
  @@ -120,6 +120,6 @@
               raise CommandError(str(error)) from error
           total = sum(rows for _, rows in exported)
           self.stdout.write(
  -            self.style.SUCCESS(f'Exported {total} rows across {len(exported)} mapped tables.')
  +            self.style.SUCCESS(f'XXExported {total} rows across {len(exported)} mapped tables.XX')
           )
  ```

