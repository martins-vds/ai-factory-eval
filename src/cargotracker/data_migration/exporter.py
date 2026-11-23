import csv
from datetime import UTC, date, datetime
from pathlib import Path

import yaml
from django.apps import apps


class DataExportError(Exception):
    pass


def _read_mapping(mapping_path):
    path = Path(mapping_path)
    try:
        mapping = yaml.safe_load(path.read_text(encoding='utf-8'))
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{path}: unable to read mapping: {error}') from error
    if mapping is None:
        mapping = {}
    if not isinstance(mapping, dict):
        raise DataExportError(f'{path}: mapping must be an object')

    specs = mapping.get('tables')
    if not isinstance(specs, list) or not specs:
        raise DataExportError('mapping has no tables')
    return specs


def _model_index():
    return {
        model._meta.db_table: model
        for model in apps.get_models()
        if not model._meta.proxy and not model._meta.auto_created
    }


def _field_for_column(model, column):
    if not isinstance(column, str):
        raise DataExportError(f'{model._meta.db_table}: mapped target columns must be strings')
    for field in model._meta.concrete_fields:
        if column in (field.column, field.name, field.attname):
            return field
    raise DataExportError(f'{model._meta.db_table}: no target column {column!r}')


def _prepare_tables(specs):
    models = _model_index()
    prepared = []
    seen_targets = set()
    for spec in specs:
        if not isinstance(spec, dict):
            raise DataExportError('each mapped table must be an object')
        target = spec.get('target')
        if not isinstance(target, str) or not target or '/' in target or '\\' in target:
            raise DataExportError(f'invalid target table name {target!r}')
        if target in seen_targets:
            raise DataExportError(f'mapping targets must be unique table names: {target}')
        seen_targets.add(target)

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
        return r'\N'
    if isinstance(value, datetime):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def export_snapshot(mapping_path, output_path):
    specs = _read_mapping(mapping_path)
    tables = _prepare_tables(specs)
    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
        exported = []
        for target, model, columns, fields in tables:
            count = 0
            with (output / f'{target}.csv').open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                rows = model._base_manager.order_by(model._meta.pk.name).values_list(
                    *(field.attname for field in fields)
                )
                for row in rows.iterator():
                    writer.writerow([_format_value(value) for value in row])
                    count += 1
            exported.append((target, count))
    except OSError as error:
        raise DataExportError(f'{output}: unable to write export: {error}') from error
    return exported
