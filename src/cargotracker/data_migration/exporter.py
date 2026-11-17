import csv
import datetime
from pathlib import Path

import yaml
from django.apps import apps


class DataExportError(Exception):
    pass


def _read_mapping(mapping_path):
    path = Path(mapping_path)
    try:
        mapping = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{path}: unable to read mapping: {error}') from error
    if not isinstance(mapping, dict):
        raise DataExportError(f'{path}: mapping must be an object')
    tables = mapping.get('tables')
    if not isinstance(tables, list) or not tables:
        raise DataExportError('mapping has no tables')
    return tables


def _model_index():
    return {
        model._meta.db_table: model
        for model in apps.get_models()
        if not model._meta.proxy and not model._meta.auto_created
    }


def _field_for_column(model, column):
    if not isinstance(column, str):
        raise DataExportError(f'{model._meta.db_table}: mapped columns must be names')
    for field in model._meta.concrete_fields:
        if column in (field.column, field.name, field.attname):
            return field
    raise DataExportError(f'{model._meta.db_table}: no target column {column!r}')


def _serialize(value):
    if value is None:
        return r'\N'
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.UTC)
        return value.astimezone(datetime.UTC).isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


def export_snapshot(mapping_path, output_path):
    tables = _read_mapping(mapping_path)
    models = _model_index()
    targets = [table.get('target') for table in tables if isinstance(table, dict)]
    if len(targets) != len(tables) or any(not isinstance(target, str) for target in targets):
        raise DataExportError('mapping targets must be table names')
    if len(targets) != len(set(targets)):
        raise DataExportError('mapping targets must be unique table names')

    prepared = []
    for table in tables:
        target = table['target']
        model = models.get(target)
        if model is None:
            raise DataExportError(f'{target}: no registered Django model for target table')
        columns = table.get('columns')
        if not isinstance(columns, dict) or not columns:
            raise DataExportError(f'{target}: mapping has no columns')
        fields = [_field_for_column(model, column) for column in columns]
        prepared.append((target, model, list(columns), fields))

    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise DataExportError(f'{output}: unable to create output directory: {error}') from error

    exported = []
    for target, model, columns, fields in prepared:
        path = output / f'{model._meta.db_table}.csv'
        try:
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                rows = model._base_manager.order_by(model._meta.pk.attname).values_list(
                    *(field.attname for field in fields)
                )
                count = 0
                for row in rows.iterator():
                    writer.writerow([_serialize(value) for value in row])
                    count += 1
        except OSError as error:
            raise DataExportError(f'{path}: unable to write export: {error}') from error
        exported.append((target, count))
    return exported
