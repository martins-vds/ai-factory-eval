import csv
import datetime
from pathlib import Path

import yaml
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


class DataExportError(Exception):
    pass


def _model_index():
    return {
        model._meta.db_table: model
        for model in apps.get_models()
        if not model._meta.proxy and not model._meta.auto_created
    }


def _field_for_column(model, column):
    for field in model._meta.concrete_fields:
        if column in (field.column, field.name, field.attname):
            return field
    raise DataExportError(f'{model._meta.db_table}: no target column {column!r}')


def _format_value(value):
    if value is None:
        return r'\N'
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.UTC)
        value = value.astimezone(datetime.UTC)
        return value.isoformat().replace('+00:00', 'Z')
    return str(value)


def _prepare_tables(mapping, models):
    specs = mapping.get('tables')
    if not isinstance(specs, list) or not specs:
        raise DataExportError('mapping has no tables')

    targets = set()
    prepared = []
    for spec in specs:
        if not isinstance(spec, dict):
            raise DataExportError('each mapped table must be an object')
        target = spec.get('target')
        if not isinstance(target, str) or target in targets:
            raise DataExportError('mapping targets must be unique table names')
        targets.add(target)
        model = models.get(target)
        if model is None:
            raise DataExportError(f'{target}: no registered Django model for target table')
        columns = spec.get('columns')
        if not isinstance(columns, dict) or not columns:
            raise DataExportError(f'{target}: mapping has no columns')
        fields = [_field_for_column(model, column) for column in columns]
        if model._meta.pk not in fields:
            raise DataExportError(f'{target}: mapping must include its primary key')
        prepared.append((target, model, list(columns), fields))
    return prepared


def _write_table(output_dir, target, model, columns, fields):
    path = output_dir / f'{target}.csv'
    values = [field.attname for field in fields]
    rows = model._base_manager.order_by(model._meta.pk.name).values_list(*values).iterator(
        chunk_size=1000
    )
    count = 0
    try:
        with path.open('w', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream)
            writer.writerow(columns)
            for row in rows:
                writer.writerow(_format_value(value) for value in row)
                count += 1
    except OSError as error:
        raise DataExportError(f'{path}: {error}') from error
    return target, count


def export_snapshot(mapping_path, output_path):
    mapping_file = Path(mapping_path)
    try:
        mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
    if not isinstance(mapping, dict):
        raise DataExportError(f'{mapping_file}: mapping must be an object')

    prepared = _prepare_tables(mapping, _model_index())
    output_dir = Path(output_path)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise DataExportError(f'{output_dir}: {error}') from error
    return [
        _write_table(output_dir, target, model, columns, fields)
        for target, model, columns, fields in prepared
    ]


class Command(BaseCommand):
    help = 'Export mapped target tables as a relational snapshot.'

    def add_arguments(self, parser):
        parser.add_argument('--mapping', required=True)
        parser.add_argument('--out', required=True)

    def handle(self, *args, **options):
        try:
            exported = export_snapshot(options['mapping'], options['out'])
        except DataExportError as error:
            raise CommandError(str(error)) from error
        total = sum(rows for _, rows in exported)
        self.stdout.write(
            self.style.SUCCESS(f'Exported {total} rows across {len(exported)} mapped tables.')
        )
