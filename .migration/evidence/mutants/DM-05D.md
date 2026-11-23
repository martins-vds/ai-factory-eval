# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `f415794e3aff44382d65a23c7841c416c0678532`): score 0.616, threshold 0.8, killed 53, survived 33. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

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
  ```

- `src/cargotracker/data_migration/exporter.py:20 Mutant #7`

  ```diff
  @@ -17,7 +17,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{path}: unable to read mapping: {error}') from error
       if not isinstance(mapping, dict):
  -        raise DataExportError(f'{path}: mapping must be an object')
  +        raise DataExportError(f'XX{path}: mapping must be an objectXX')
       specs = mapping.get('tables')
       if not isinstance(specs, list) or not specs:
  ```

- `src/cargotracker/data_migration/exporter.py:23 Mutant #12`

  ```diff
  @@ -20,7 +20,7 @@
           raise DataExportError(f'{path}: mapping must be an object')
       specs = mapping.get('tables')
  -    if not isinstance(specs, list) or not specs:
  +    if not isinstance(specs, list) and not specs:
           raise DataExportError('mapping has no tables')
       return specs
  ```

- `src/cargotracker/data_migration/exporter.py:24 Mutant #13`

  ```diff
  @@ -21,7 +21,7 @@
       specs = mapping.get('tables')
       if not isinstance(specs, list) or not specs:
  -        raise DataExportError('mapping has no tables')
  +        raise DataExportError('XXmapping has no tablesXX')
       return specs
  ```

- `src/cargotracker/data_migration/exporter.py:32 Mutant #16`

  ```diff
  @@ -29,7 +29,7 @@
       return {
           model._meta.db_table: model
           for model in apps.get_models()
  -        if not model._meta.proxy and not model._meta.auto_created
  +        if not model._meta.proxy or not model._meta.auto_created
       }
  ```

- `src/cargotracker/data_migration/exporter.py:38 Mutant #18`

  ```diff
  @@ -35,7 +35,7 @@
   def _field_for_column(model, column):
       if not isinstance(column, str):
  -        raise DataExportError(f'{model._meta.db_table}: mapped target columns must be strings')
  +        raise DataExportError(f'XX{model._meta.db_table}: mapped target columns must be stringsXX')
       for field in model._meta.concrete_fields:
           if column in (field.column, field.name, field.attname):
               return field
  ```

- `src/cargotracker/data_migration/exporter.py:42 Mutant #20`

  ```diff
  @@ -39,7 +39,7 @@
       for field in model._meta.concrete_fields:
           if column in (field.column, field.name, field.attname):
               return field
  -    raise DataExportError(f'{model._meta.db_table}: no target column {column!r}')
  +    raise DataExportError(f'XX{model._meta.db_table}: no target column {column!r}XX')
   def _prepare_tables(specs):
  ```

- `src/cargotracker/data_migration/exporter.py:51 Mutant #25`

  ```diff
  @@ -48,7 +48,7 @@
       seen_targets = set()
       for spec in specs:
           if not isinstance(spec, dict):
  -            raise DataExportError('each mapped table must be an object')
  +            raise DataExportError('XXeach mapped table must be an objectXX')
           target = spec.get('target')
           if not isinstance(target, str) or not target or '/' in target or '\\' in target:
               raise DataExportError(f'invalid target table name {target!r}')
  ```

- `src/cargotracker/data_migration/exporter.py:53 Mutant #30`

  ```diff
  @@ -50,7 +50,7 @@
           if not isinstance(spec, dict):
               raise DataExportError('each mapped table must be an object')
           target = spec.get('target')
  -        if not isinstance(target, str) or not target or '/' in target or '\\' in target:
  +        if not isinstance(target, str) or not target or 'XX/XX' in target or '\\' in target:
               raise DataExportError(f'invalid target table name {target!r}')
           if target in seen_targets:
               raise DataExportError(f'mapping targets must be unique table names: {target}')
  ```

- `src/cargotracker/data_migration/exporter.py:53 Mutant #32`

  ```diff
  @@ -50,7 +50,7 @@
           if not isinstance(spec, dict):
               raise DataExportError('each mapped table must be an object')
           target = spec.get('target')
  -        if not isinstance(target, str) or not target or '/' in target or '\\' in target:
  +        if not isinstance(target, str) or not target or '/' in target or 'XX\\XX' in target:
               raise DataExportError(f'invalid target table name {target!r}')
           if target in seen_targets:
               raise DataExportError(f'mapping targets must be unique table names: {target}')
  ```

- `src/cargotracker/data_migration/exporter.py:53 Mutant #34`

  ```diff
  @@ -50,7 +50,7 @@
           if not isinstance(spec, dict):
               raise DataExportError('each mapped table must be an object')
           target = spec.get('target')
  -        if not isinstance(target, str) or not target or '/' in target or '\\' in target:
  +        if not isinstance(target, str) and not target or '/' in target or '\\' in target:
               raise DataExportError(f'invalid target table name {target!r}')
           if target in seen_targets:
               raise DataExportError(f'mapping targets must be unique table names: {target}')
  ```

- `src/cargotracker/data_migration/exporter.py:54 Mutant #35`

  ```diff
  @@ -51,7 +51,7 @@
               raise DataExportError('each mapped table must be an object')
           target = spec.get('target')
           if not isinstance(target, str) or not target or '/' in target or '\\' in target:
  -            raise DataExportError(f'invalid target table name {target!r}')
  +            raise DataExportError(f'XXinvalid target table name {target!r}XX')
           if target in seen_targets:
               raise DataExportError(f'mapping targets must be unique table names: {target}')
           seen_targets.add(target)
  ```

- `src/cargotracker/data_migration/exporter.py:56 Mutant #37`

  ```diff
  @@ -53,7 +53,7 @@
           if not isinstance(target, str) or not target or '/' in target or '\\' in target:
               raise DataExportError(f'invalid target table name {target!r}')
           if target in seen_targets:
  -            raise DataExportError(f'mapping targets must be unique table names: {target}')
  +            raise DataExportError(f'XXmapping targets must be unique table names: {target}XX')
           seen_targets.add(target)
           model = models.get(target)
  ```

- `src/cargotracker/data_migration/exporter.py:61 Mutant #40`

  ```diff
  @@ -58,7 +58,7 @@
           model = models.get(target)
           if model is None:
  -            raise DataExportError(f'{target}: no registered Django model for target table')
  +            raise DataExportError(f'XX{target}: no registered Django model for target tableXX')
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
               raise DataExportError(f'{target}: mapping has no columns')
  ```

- `src/cargotracker/data_migration/exporter.py:63 Mutant #45`

  ```diff
  @@ -60,7 +60,7 @@
           if model is None:
               raise DataExportError(f'{target}: no registered Django model for target table')
           columns = spec.get('columns')
  -        if not isinstance(columns, dict) or not columns:
  +        if not isinstance(columns, dict) and not columns:
               raise DataExportError(f'{target}: mapping has no columns')
           fields = [_field_for_column(model, column) for column in columns]
           if model._meta.pk not in fields:
  ```

- `src/cargotracker/data_migration/exporter.py:64 Mutant #46`

  ```diff
  @@ -61,7 +61,7 @@
               raise DataExportError(f'{target}: no registered Django model for target table')
           columns = spec.get('columns')
           if not isinstance(columns, dict) or not columns:
  -            raise DataExportError(f'{target}: mapping has no columns')
  +            raise DataExportError(f'XX{target}: mapping has no columnsXX')
           fields = [_field_for_column(model, column) for column in columns]
           if model._meta.pk not in fields:
               raise DataExportError(f'{target}: mapping must include its primary key')
  ```

- `src/cargotracker/data_migration/exporter.py:67 Mutant #49`

  ```diff
  @@ -64,7 +64,7 @@
               raise DataExportError(f'{target}: mapping has no columns')
           fields = [_field_for_column(model, column) for column in columns]
           if model._meta.pk not in fields:
  -            raise DataExportError(f'{target}: mapping must include its primary key')
  +            raise DataExportError(f'XX{target}: mapping must include its primary keyXX')
           prepared.append((target, model, list(columns), fields))
       return prepared
  ```

- `src/cargotracker/data_migration/exporter.py:76 Mutant #52`

  ```diff
  @@ -73,7 +73,7 @@
       if value is None:
           return r'\N'
       if isinstance(value, datetime):
  -        if value.utcoffset() is None:
  +        if value.utcoffset() is not None:
               value = value.replace(tzinfo=UTC)
           return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, date):
  ```

- `src/cargotracker/data_migration/exporter.py:77 Mutant #53`

  ```diff
  @@ -74,7 +74,7 @@
           return r'\N'
       if isinstance(value, datetime):
           if value.utcoffset() is None:
  -            value = value.replace(tzinfo=UTC)
  +            value = None
           return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, date):
           return value.isoformat()
  ```

- `src/cargotracker/data_migration/exporter.py:89 Mutant #59`

  ```diff
  @@ -86,7 +86,7 @@
       tables = _prepare_tables(specs)
       output = Path(output_path)
       try:
  -        output.mkdir(parents=True, exist_ok=True)
  +        output.mkdir(parents=False, exist_ok=True)
           exported = []
           for target, model, columns, fields in tables:
               count = 0
  ```

- `src/cargotracker/data_migration/exporter.py:89 Mutant #60`

  ```diff
  @@ -86,7 +86,7 @@
       tables = _prepare_tables(specs)
       output = Path(output_path)
       try:
  -        output.mkdir(parents=True, exist_ok=True)
  +        output.mkdir(parents=True, exist_ok=False)
           exported = []
           for target, model, columns, fields in tables:
               count = 0
  ```

- `src/cargotracker/data_migration/exporter.py:92 Mutant #62`

  ```diff
  @@ -89,7 +89,7 @@
           output.mkdir(parents=True, exist_ok=True)
           exported = []
           for target, model, columns, fields in tables:
  -            count = 0
  +            count = 1
               with (output / f'{target}.csv').open('w', newline='', encoding='utf-8') as stream:
                   writer = csv.writer(stream)
                   writer.writerow(columns)
  ```

- `src/cargotracker/data_migration/exporter.py:99 Mutant #71`

  ```diff
  @@ -96,7 +96,7 @@
                   rows = model._base_manager.order_by(model._meta.pk.name).values_list(
                       *(field.attname for field in fields)
                   )
  -                for row in rows.iterator(chunk_size=1000):
  +                for row in rows.iterator(chunk_size=1001):
                       writer.writerow([_format_value(value) for value in row])
                       count += 1
               exported.append((target, count))
  ```

- `src/cargotracker/data_migration/exporter.py:101 Mutant #72`

  ```diff
  @@ -98,7 +98,7 @@
                   )
                   for row in rows.iterator(chunk_size=1000):
                       writer.writerow([_format_value(value) for value in row])
  -                    count += 1
  +                    count = 1
               exported.append((target, count))
       except OSError as error:
           raise DataExportError(f'{output}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:101 Mutant #73`

  ```diff
  @@ -98,7 +98,7 @@
                   )
                   for row in rows.iterator(chunk_size=1000):
                       writer.writerow([_format_value(value) for value in row])
  -                    count += 1
  +                    count -= 1
               exported.append((target, count))
       except OSError as error:
           raise DataExportError(f'{output}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:101 Mutant #74`

  ```diff
  @@ -98,7 +98,7 @@
                   )
                   for row in rows.iterator(chunk_size=1000):
                       writer.writerow([_format_value(value) for value in row])
  -                    count += 1
  +                    count += 2
               exported.append((target, count))
       except OSError as error:
           raise DataExportError(f'{output}: unable to write export: {error}') from error
  ```

- `src/cargotracker/data_migration/exporter.py:104 Mutant #75`

  ```diff
  @@ -101,6 +101,6 @@
                       count += 1
               exported.append((target, count))
       except OSError as error:
  -        raise DataExportError(f'{output}: unable to write export: {error}') from error
  +        raise DataExportError(f'XX{output}: unable to write export: {error}XX') from error
       return exported
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

