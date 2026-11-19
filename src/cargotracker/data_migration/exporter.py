import csv
import datetime
from pathlib import Path

import yaml
from django.apps import apps


class DataExportError(Exception):
    pass


def _read_mapping(mapping_path):
    mapping_file = Path(mapping_path)
    try:
        mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8'))
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
    if not isinstance(mapping, dict):
        raise DataExportError(f'{mapping_file}: mapping must be an object')
    return mapping


def _field_for_column(model, column):
    for field in model._meta.concrete_fields:
        if column in (field.column, field.name, field.attname):
            return field
    raise DataExportError(f'{model._meta.db_table}: no target column {column!r}')


def _mapped_tables(mapping):
    specs = mapping.get('tables')
    if not isinstance(specs, list) or not specs:
        raise DataExportError('mapping has no tables')

    models = {
        model._meta.db_table: model
        for model in apps.get_models()
        if not model._meta.proxy and not model._meta.auto_created
    }
    mapped = []
    targets = set()
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
        fields = [(column, _field_for_column(model, column)) for column in columns]
        if model._meta.pk not in (field for _, field in fields):
            raise DataExportError(f'{target}: mapping must include its primary key')
        mapped.append((target, model, fields))
    return mapped


def _csv_value(value):
    if value is None:
        return r'\N'
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.UTC)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def export_snapshot(mapping_path, output_directory):
    mapping = _read_mapping(mapping_path)
    tables = _mapped_tables(mapping)
    output = Path(output_directory)
    try:
        output.mkdir(parents=True, exist_ok=True)
        row_counts = []
        for target, model, fields in tables:
            path = output / f'{target}.csv'
            rows_written = 0
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(column for column, _ in fields)
                values = model._base_manager.order_by(model._meta.pk.attname).values_list(
                    *(field.attname for _, field in fields)
                )
                for row in values.iterator(chunk_size=1000):
                    writer.writerow(_csv_value(value) for value in row)
                    rows_written += 1
            row_counts.append((target, rows_written))
    except OSError as error:
        raise DataExportError(f'{output}: unable to write export: {error}') from error
    return row_counts
