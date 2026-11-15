import csv
import datetime
from pathlib import Path

import yaml
from django.apps import apps
from django.db import models

NULL_MARKER = r'\N'


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


def _mapped_tables(mapping, models_by_table):
    specs = mapping.get('tables')
    if not isinstance(specs, list) or not specs:
        raise DataExportError('mapping has no tables')

    targets = [spec.get('target') for spec in specs]
    if (
        any(not isinstance(target, str) for target in targets)
        or len(targets) != len(set(targets))
    ):
        raise DataExportError('mapping targets must be unique table names')

    prepared = []
    for spec in specs:
        target = spec['target']
        model = models_by_table.get(target)
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


def _format_value(value, field):
    if value is None:
        return NULL_MARKER
    if isinstance(field, models.DateTimeField):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=datetime.UTC)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(field, models.DateField):
        return value.isoformat()
    return str(value)


def export_snapshot(mapping_path, output_path):
    mapping_file = Path(mapping_path)
    try:
        mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
    if not isinstance(mapping, dict):
        raise DataExportError(f'{mapping_file}: mapping must be an object')

    prepared = _mapped_tables(mapping, _model_index())
    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise DataExportError(f'{output}: unable to create output directory: {error}') from error

    exported = []
    for target, model, columns, fields in prepared:
        path = output / f'{target}.csv'
        count = 0
        try:
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                rows = model._base_manager.order_by(model._meta.pk.name).values_list(
                    *(field.attname for field in fields)
                )
                for row in rows:
                    writer.writerow(
                        [_format_value(value, field) for value, field in zip(row, fields)]
                    )
                    count += 1
        except OSError as error:
            raise DataExportError(f'{path}: unable to write export: {error}') from error
        exported.append((target, count))
    return exported
