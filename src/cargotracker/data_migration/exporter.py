import csv
import datetime
import decimal
from pathlib import Path

import yaml
from django.apps import apps


class DataExportError(Exception):
    pass


def _read_mapping(mapping_path):
    mapping_file = Path(mapping_path)
    try:
        mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
    if not isinstance(mapping, dict):
        raise DataExportError(f'{mapping_file}: mapping must be an object')
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
    if any(not isinstance(target, str) or not target for target in targets) or len(targets) != len(
        set(targets)
    ):
        raise DataExportError('mapping targets must be unique table names')

    prepared = []
    for spec in specs:
        target = spec['target']
        if Path(target).name != target or '/' in target or '\\' in target:
            raise DataExportError(f'{target}: invalid target table name')
        model = models.get(target)
        if model is None:
            raise DataExportError(f'{target}: no registered Django model for target table')

        columns = spec.get('columns')
        if not isinstance(columns, dict) or not columns:
            raise DataExportError(f'{target}: mapping has no columns')

        fields = []
        for column, definition in columns.items():
            if isinstance(definition, dict):
                source_column = definition.get('from')
            else:
                source_column = definition
            if not isinstance(column, str) or not isinstance(source_column, str):
                raise DataExportError(f'{target}: mapping must name target and source columns')
            fields.append((column, _field_for_column(model, column)))

        prepared.append((target, model, fields))
    return prepared


def _format_value(value):
    if value is None:
        return r'\N'
    if isinstance(value, datetime.datetime):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=datetime.UTC)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, decimal.Decimal):
        return str(value)
    return value


def export_snapshot(mapping_path, output_path):
    mapping = _read_mapping(mapping_path)
    tables = _prepare_tables(mapping, _model_index())
    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
        exported = []
        for target, model, columns in tables:
            path = output / f'{target}.csv'
            field_names = [field.attname for _, field in columns]
            row_count = 0
            with path.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow([column for column, _ in columns])
                rows = model._base_manager.order_by('pk').values_list(*field_names)
                for row in rows:
                    writer.writerow([_format_value(value) for value in row])
                    row_count += 1
            exported.append((target, row_count))
    except OSError as error:
        raise DataExportError(f'{output}: unable to write export: {error}') from error
    return exported
