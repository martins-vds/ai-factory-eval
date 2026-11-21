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
    return mapping


def _model_index():
    return {
        model._meta.db_table: model
        for model in apps.get_models()
        if not model._meta.proxy and not model._meta.auto_created
    }


def _prepare_tables(mapping):
    specs = mapping.get('tables')
    if (
        not isinstance(specs, list)
        or not specs
        or any(not isinstance(spec, dict) for spec in specs)
    ):
        raise DataExportError('mapping has no tables')

    targets = [spec.get('target') for spec in specs]
    if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
        raise DataExportError('mapping targets must be unique table names')

    models = _model_index()
    prepared = []
    for spec in specs:
        target = spec['target']
        if Path(target).name != target or target in ('.', '..'):
            raise DataExportError(f'{target}: invalid target table name')
        model = models.get(target)
        if model is None:
            raise DataExportError(f'{target}: no registered Django model for target table')

        columns = spec.get('columns')
        if not isinstance(columns, dict) or not columns:
            raise DataExportError(f'{target}: mapping has no columns')
        fields = []
        for column in columns:
            field = next(
                (
                    candidate
                    for candidate in model._meta.concrete_fields
                    if column in (candidate.column, candidate.name, candidate.attname)
                ),
                None,
            )
            if field is None:
                raise DataExportError(f'{target}: no target column {column!r}')
            fields.append(field)
        if model._meta.pk not in fields:
            raise DataExportError(f'{target}: mapping must include its primary key')
        prepared.append((target, model, fields))
    return prepared


def _format_value(value):
    if value is None:
        return r'\N'
    if isinstance(value, datetime.datetime):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=datetime.UTC)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, (datetime.date, datetime.time)):
        return value.isoformat()
    return str(value)


def export_snapshot(mapping_path, output_path):
    mapping = _read_mapping(mapping_path)
    tables = _prepare_tables(mapping)
    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise DataExportError(f'{output}: unable to create output directory: {error}') from error

    exported = []
    for target, model, fields in tables:
        path = output / f'{target}.csv'
        try:
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow([field.column for field in fields])
                rows = model._base_manager.order_by(model._meta.pk.name).values_list(
                    *(field.attname for field in fields)
                )
                writer.writerows(
                    [_format_value(value) for value in row]
                    for row in rows.iterator(chunk_size=1000)
                )
        except OSError as error:
            raise DataExportError(f'{path}: unable to write export: {error}') from error
        exported.append(target)
    return exported
