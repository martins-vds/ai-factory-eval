# Surviving mutants: DM-05D

Written by `afs-mutation` on its last run (base `f415794e3aff44382d65a23c7841c416c0678532`): score 0.930, threshold 0.8, killed 80, survived 6. Each line is a mutant no test killed: add a test that fails on it, or simplify the code if it is equivalent. The diff under each line is the change mutmut made.

- `src/cargotracker/data_migration/exporter.py:20 Mutant #6`

  ```diff
  @@ -17,7 +17,7 @@
       except (OSError, yaml.YAMLError) as error:
           raise DataExportError(f'{path}: unable to read mapping: {error}') from error
       if mapping is None:
  -        mapping = {}
  +        mapping = None
       if not isinstance(mapping, dict):
           raise DataExportError(f'{path}: mapping must be an object')
  ```

- `src/cargotracker/data_migration/exporter.py:34 Mutant #17`

  ```diff
  @@ -31,7 +31,7 @@
       return {
           model._meta.db_table: model
           for model in apps.get_models()
  -        if not model._meta.proxy and not model._meta.auto_created
  +        if not model._meta.proxy or not model._meta.auto_created
       }
  ```

- `src/cargotracker/data_migration/exporter.py:55 Mutant #35`

  ```diff
  @@ -52,7 +52,7 @@
           if not isinstance(spec, dict):
               raise DataExportError('each mapped table must be an object')
           target = spec.get('target')
  -        if not isinstance(target, str) or not target or '/' in target or '\\' in target:
  +        if not isinstance(target, str) and not target or '/' in target or '\\' in target:
               raise DataExportError(f'invalid target table name {target!r}')
           if target in seen_targets:
               raise DataExportError(f'mapping targets must be unique table names: {target}')
  ```

- `src/cargotracker/data_migration/exporter.py:78 Mutant #53`

  ```diff
  @@ -75,7 +75,7 @@
       if value is None:
           return r'\N'
       if isinstance(value, datetime):
  -        if value.utcoffset() is None:
  +        if value.utcoffset() is not None:
               value = value.replace(tzinfo=UTC)
           return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, date):
  ```

- `src/cargotracker/data_migration/exporter.py:79 Mutant #54`

  ```diff
  @@ -76,7 +76,7 @@
           return r'\N'
       if isinstance(value, datetime):
           if value.utcoffset() is None:
  -            value = value.replace(tzinfo=UTC)
  +            value = None
           return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')
       if isinstance(value, date):
           return value.isoformat()
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

