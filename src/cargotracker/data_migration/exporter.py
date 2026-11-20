import csv
import datetime
from pathlib import Path

import yaml
from django.apps import apps

NULL_MARKER = r'\N'


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
    return mapping


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


def _prepare_tables(mapping, models):
    specs = mapping.get('tables')
    if not isinstance(specs, list) or not specs:
        raise DataExportError('mapping has no tables')
    targets = [spec.get('target') if isinstance(spec, dict) else None for spec in specs]
    if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
        raise DataExportError('mapping targets must be unique table names')

    prepared = []
    for target, spec in zip(targets, specs):
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


def _format_value(value):
    if value is None:
        return NULL_MARKER
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, datetime.datetime):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=datetime.UTC)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, datetime.date):
        return value.isoformat()
    return str(value)


def export_snapshot(mapping_path, output_path):
    mapping = _read_mapping(mapping_path)
    tables = _prepare_tables(mapping, _model_index())
    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise DataExportError(f'{output}: unable to create output directory: {error}') from error

    row_counts = []
    for target, model, columns, fields in tables:
        path = output / f'{target}.csv'
        count = 0
        try:
            with path.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                rows = model._base_manager.order_by(model._meta.pk.name).values_list(
                    *(field.attname for field in fields)
                )
                for row in rows:
                    writer.writerow([_format_value(value) for value in row])
                    count += 1
        except OSError as error:
            raise DataExportError(f'{path}: unable to write target export: {error}') from error
        row_counts.append((target, count))
    return row_counts
