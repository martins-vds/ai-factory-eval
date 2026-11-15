import csv
import datetime
from pathlib import Path

import yaml
from django.apps import apps


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
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, datetime.date):
        return value.isoformat()
    return str(value)


def _mapped_tables(mapping):
    specs = mapping.get('tables')
    if not isinstance(specs, list) or not specs:
        raise DataExportError('mapping has no tables')

    models = _model_index()
    tables = []
    targets = set()
    for spec in specs:
        if not isinstance(spec, dict):
            raise DataExportError('mapping tables must be objects')
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
        fields = {column: _field_for_column(model, column) for column in columns}
        if model._meta.pk not in fields.values():
            raise DataExportError(f'{target}: mapping must include its primary key')
        tables.append((target, model, columns, fields))
    return tables


def export_snapshot(mapping_path, output_path):
    mapping_file = Path(mapping_path)
    try:
        mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
    if not isinstance(mapping, dict):
        raise DataExportError(f'{mapping_file}: mapping must be an object')

    tables = _mapped_tables(mapping)
    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
        for target, model, columns, fields in tables:
            path = output / f'{target}.csv'
            field_names = [fields[column].attname for column in columns]
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream, quoting=csv.QUOTE_ALL)
                writer.writerow(columns)
                rows = model._base_manager.order_by(model._meta.pk.name).values(*field_names)
                for row in rows:
                    writer.writerow(
                        [_format_value(row[field_name]) for field_name in field_names]
                    )
    except OSError as error:
        raise DataExportError(f'{output}: unable to write export: {error}') from error

