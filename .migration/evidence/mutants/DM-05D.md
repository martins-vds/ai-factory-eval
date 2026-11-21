# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `8e1d44445d0f0fc41e10b9ada87f80d9f18dd60f`): score 0.659, threshold 0.8, killed 54, survived 28. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:18 Mutant #5`

  ```diff
  @@ -15,7 +15,7 @@
       try:
           mapping = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
       except (OSError, yaml.YAMLError) as error:
  -        raise DataExportError(f'{path}: unable to read mapping: {error}') from error
  +        raise DataExportError(f'XX{path}: unable to read mapping: {error}XX') from error
       if not isinstance(mapping, dict):
           raise DataExportError(f'{path}: mapping must be an object')
       return mapping
  ```

- `src/cargotracker/data_migration/exporter.py:20 Mutant #7`

  ```diff
  @@ -17,7 +17,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{path}: unable to read mapping: {error}') from error
       if not isinstance(mapping, dict):
  -        raise DataExportError(f'{path}: mapping must be an object')
  +        raise DataExportError(f'XX{path}: mapping must be an objectXX')
       return mapping
  ```

- `src/cargotracker/data_migration/exporter.py:28 Mutant #10`

  ```diff
  @@ -25,7 +25,7 @@
       return {
           model._meta.db_table: model
           for model in apps.get_models()
  -        if not model._meta.proxy and not model._meta.auto_created
  +        if not model._meta.proxy or not model._meta.auto_created
       }
  ```

- `src/cargotracker/data_migration/exporter.py:37 Mutant #16`

  ```diff
  @@ -32,8 +32,7 @@
   def _prepare_tables(mapping):
       specs = mapping.get('tables')
       if (
  -        not isinstance(specs, list)
  -        or not specs
  +        not isinstance(specs, list) and not specs
           or any(not isinstance(spec, dict) for spec in specs)
       ):
           raise DataExportError('mapping has no tables')
  ```

- `src/cargotracker/data_migration/exporter.py:39 Mutant #17`

  ```diff
  @@ -36,7 +36,7 @@
           or not specs
           or any(not isinstance(spec, dict) for spec in specs)
       ):
  -        raise DataExportError('mapping has no tables')
  +        raise DataExportError('XXmapping has no tablesXX')
       targets = [spec.get('target') for spec in specs]
       if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
  ```

- `src/cargotracker/data_migration/exporter.py:42 Mutant #22`

  ```diff
  @@ -39,7 +39,7 @@
           raise DataExportError('mapping has no tables')
       targets = [spec.get('target') for spec in specs]
  -    if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
  +    if any(not isinstance(target, str) for target in targets) and len(targets) != len(set(targets)):
           raise DataExportError('mapping targets must be unique table names')
       models = _model_index()
  ```

- `src/cargotracker/data_migration/exporter.py:43 Mutant #23`

  ```diff
  @@ -40,7 +40,7 @@
       targets = [spec.get('target') for spec in specs]
       if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
  -        raise DataExportError('mapping targets must be unique table names')
  +        raise DataExportError('XXmapping targets must be unique table namesXX')
       models = _model_index()
       prepared = []
  ```

- `src/cargotracker/data_migration/exporter.py:49 Mutant #30`

  ```diff
  @@ -46,7 +46,7 @@
       prepared = []
       for spec in specs:
           target = spec['target']
  -        if Path(target).name != target or target in ('.', '..'):
  +        if Path(target).name != target or target in ('XX.XX', '..'):
               raise DataExportError(f'{target}: invalid target table name')
           model = models.get(target)
           if model is None:
  ```

- `src/cargotracker/data_migration/exporter.py:49 Mutant #31`

  ```diff
  @@ -46,7 +46,7 @@
       prepared = []
       for spec in specs:
           target = spec['target']
  -        if Path(target).name != target or target in ('.', '..'):
  +        if Path(target).name != target or target in ('.', 'XX..XX'):
               raise DataExportError(f'{target}: invalid target table name')
           model = models.get(target)
           if model is None:
  ```

- `src/cargotracker/data_migration/exporter.py:49 Mutant #32`

  ```diff
  @@ -46,7 +46,7 @@
       prepared = []
       for spec in specs:
           target = spec['target']
  -        if Path(target).name != target or target in ('.', '..'):
  +        if Path(target).name != target and target in ('.', '..'):
               raise DataExportError(f'{target}: invalid target table name')
           model = models.get(target)
           if model is None:
  ```

- `src/cargotracker/data_migration/exporter.py:50 Mutant #33`

  ```diff
  @@ -47,7 +47,7 @@
       for spec in specs:
           target = spec['target']
           if Path(target).name != target or target in ('.', '..'):
  -            raise DataExportError(f'{target}: invalid target table name')
  +            raise DataExportError(f'XX{target}: invalid target table nameXX')
           model = models.get(target)
           if model is None:
               raise DataExportError(f'{target}: no registered Django model for target table')
  ```

- `src/cargotracker/data_migration/exporter.py:53 Mutant #36`

  ```diff
  @@ -50,7 +50,7 @@
               raise DataExportError(f'{target}: invalid target table name')
           model = models.get(target)
           if model is None:
  -            raise DataExportError(f'{target}: no registered Django model for target table')
  +            raise DataExportError(f'XX{target}: no registered Django model for target tableXX')
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
  ```

- `src/cargotracker/data_migration/exporter.py:56 Mutant #41`

  ```diff
  @@ -53,7 +53,7 @@
               raise DataExportError(f'{target}: no registered Django model for target table')
           columns = spec.get('columns')
  -        if not isinstance(columns, dict) or not columns:
  +        if not isinstance(columns, dict) and not columns:
               raise DataExportError(f'{target}: mapping has no columns')
           fields = []
           for column in columns:
  ```

- `src/cargotracker/data_migration/exporter.py:57 Mutant #42`

  ```diff
  @@ -54,7 +54,7 @@
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
  -            raise DataExportError(f'{target}: mapping has no columns')
  +            raise DataExportError(f'XX{target}: mapping has no columnsXX')
           fields = []
           for column in columns:
               field = next(
  ```

- `src/cargotracker/data_migration/exporter.py:69 Mutant #47`

  ```diff
  @@ -66,7 +66,7 @@
                   None,
               )
               if field is None:
  -                raise DataExportError(f'{target}: no target column {column!r}')
  +                raise DataExportError(f'XX{target}: no target column {column!r}XX')
               fields.append(field)
           if model._meta.pk not in fields:
               raise DataExportError(f'{target}: mapping must include its primary key')
  ```

- `src/cargotracker/data_migration/exporter.py:72 Mutant #49`

  ```diff
  @@ -69,7 +69,7 @@
                   raise DataExportError(f'{target}: no target column {column!r}')
               fields.append(field)
           if model._meta.pk not in fields:
  -            raise DataExportError(f'{target}: mapping must include its primary key')
  +            raise DataExportError(f'XX{target}: mapping must include its primary keyXX')
           prepared.append((target, model, fields, list(columns)))
       return prepared
  ```

- `src/cargotracker/data_migration/exporter.py:81 Mutant #52`

  ```diff
  @@ -78,7 +78,7 @@
       if value is None:
           return r'\N'
       if isinstance(value, datetime.datetime):
  -        if value.utcoffset() is None:
  +        if value.utcoffset() is not None:
               value = value.replace(tzinfo=datetime.UTC)
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, (datetime.date, datetime.time)):
  ```

- `src/cargotracker/data_migration/exporter.py:82 Mutant #53`

  ```diff
  @@ -79,7 +79,7 @@
           return r'\N'
       if isinstance(value, datetime.datetime):
           if value.utcoffset() is None:
  -            value = value.replace(tzinfo=datetime.UTC)
  +            value = None
           return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, (datetime.date, datetime.time)):
           return value.isoformat()
  ```

- `src/cargotracker/data_migration/exporter.py:94 Mutant #59`

  ```diff
  @@ -91,7 +91,7 @@
       tables = _prepare_tables(mapping)
       output = Path(output_path)
       try:
  -        output.mkdir(parents=True, exist_ok=True)
  +        output.mkdir(parents=False, exist_ok=True)
       except OSError as error:
           raise DataExportError(f'{output}: unable to create output directory: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:94 Mutant #60`

  ```diff
  @@ -91,7 +91,7 @@
       tables = _prepare_tables(mapping)
       output = Path(output_path)
       try:
  -        output.mkdir(parents=True, exist_ok=True)
  +        output.mkdir(parents=True, exist_ok=False)
       except OSError as error:
           raise DataExportError(f'{output}: unable to create output directory: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:96 Mutant #61`

  ```diff
  @@ -93,7 +93,7 @@
       try:
           output.mkdir(parents=True, exist_ok=True)
       except OSError as error:
  -        raise DataExportError(f'{output}: unable to create output directory: {error}') from error
  +        raise DataExportError(f'XX{output}: unable to create output directory: {error}XX') from error
       exported = []
       for target, model, fields, columns in tables:
  ```

- `src/cargotracker/data_migration/exporter.py:110 Mutant #71`

  ```diff
  @@ -107,7 +107,7 @@
                   )
                   writer.writerows(
                       [_format_value(value) for value in row]
  -                    for row in rows.iterator(chunk_size=1000)
  +                    for row in rows.iterator(chunk_size=1001)
                   )
           except OSError as error:
               raise DataExportError(f'{path}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:113 Mutant #72`

  ```diff
  @@ -110,7 +110,7 @@
                       for row in rows.iterator(chunk_size=1000)
                   )
           except OSError as error:
  -            raise DataExportError(f'{path}: unable to write export: {error}') from error
  +            raise DataExportError(f'XX{path}: unable to write export: {error}XX') from error
           exported.append(target)
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

- `src/cargotracker/data_migration/management/commands/export_data_snapshot.py:10 Mutant #4`

  ```diff
  @@ -7,7 +7,7 @@
       help = 'Export mapped target tables as snapshot-format CSV files.'
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
  @@ -15,5 +15,5 @@
               exported = export_snapshot(options['mapping'], options['out'])
           except DataExportError as error:
               raise CommandError(str(error)) from error
  -        self.stdout.write(self.style.SUCCESS(f'Exported {len(exported)} mapped tables.'))
  +        self.stdout.write(self.style.SUCCESS(f'XXExported {len(exported)} mapped tables.XX'))
  ```

