import csv
import datetime
from pathlib import Path

import yaml
from django.apps import apps
from django.db import connection

NULL_MARKER = r'\N'


class DataExportError(Exception):
    pass


def _models_by_table():
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


def _serialize(value):
    if value is None:
        return NULL_MARKER
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.UTC)
        return value.astimezone(datetime.UTC).isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    return str(value)


def _export_table(spec, models, output):
    target = spec.get('target')
    model = models.get(target)
    if model is None:
        raise DataExportError(f'{target}: no registered Django model for target table')

    columns = spec.get('columns')
    if not isinstance(columns, dict) or not columns:
        raise DataExportError(f'{target}: mapping has no columns')
    fields = [_field_for_column(model, column) for column in columns]
    field_names = [field.attname for field in fields]
    path = output / f'{target}.csv'
    try:
        with path.open('w', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream, quoting=csv.QUOTE_ALL, lineterminator='\n')
            writer.writerow(columns)
            rows = model._base_manager.order_by(model._meta.pk.attname).values(*field_names)
            count = 0
            for row in rows.iterator():
                writer.writerow(_serialize(row[field]) for field in field_names)
                count += 1
    except OSError as error:
        raise DataExportError(f'{path}: {error}') from error
    return target, count


def export_snapshot(mapping_path, output_path):
    if connection.vendor != 'postgresql':
        raise DataExportError('export_data_snapshot requires PostgreSQL')

    mapping_file = Path(mapping_path)
    try:
        mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
    if not isinstance(mapping, dict):
        raise DataExportError(f'{mapping_file}: mapping must be an object')

    specs = mapping.get('tables')
    if not isinstance(specs, list) or not specs:
        raise DataExportError('mapping has no tables')
    targets = [spec.get('target') if isinstance(spec, dict) else None for spec in specs]
    if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
        raise DataExportError('mapping targets must be unique table names')

    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise DataExportError(f'{output}: unable to create output directory: {error}') from error

    models = _models_by_table()
    return [_export_table(spec, models, output) for spec in specs]
