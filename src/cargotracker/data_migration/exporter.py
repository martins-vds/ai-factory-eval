import csv
import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml
from django.apps import apps

NULL_MARKER = r'\N'


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


def _mapping_timezone(mapping):
    defaults = mapping.get('defaults') or {}
    if not isinstance(defaults, dict):
        raise DataExportError('mapping defaults must be an object')
    zone = defaults.get('timestamp_tz', 'UTC')
    try:
        return ZoneInfo(zone)
    except (TypeError, ZoneInfoNotFoundError) as error:
        raise DataExportError(f'unknown timestamp timezone {zone!r}') from error


def _model_index():
    return {model._meta.db_table: model for model in apps.get_models() if not model._meta.proxy}


def _field_for_column(model, column):
    for field in model._meta.concrete_fields:
        if column in (field.column, field.name, field.attname):
            return field
    raise DataExportError(f'{model._meta.db_table}: no target column {column!r}')


def _mapped_tables(mapping, models):
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
        if Path(target).name != target or target == '..':
            raise DataExportError(f'{target!r}: invalid target table name')
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


def _serialize(value, timezone):
    if value is None:
        return NULL_MARKER
    if isinstance(value, datetime.datetime):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=timezone)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


def export_snapshot(mapping_path, output_dir):
    mapping = _read_mapping(mapping_path)
    timezone = _mapping_timezone(mapping)
    tables = _mapped_tables(mapping, _model_index())

    directory = Path(output_dir)
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise DataExportError(f'{directory}: unable to create output directory: {error}') from error

    results = []
    for target, model, columns, fields in tables:
        path = directory / f'{target}.csv'
        try:
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                rows = (
                    model._base_manager.order_by(model._meta.pk.name)
                    .values_list(*(field.attname for field in fields))
                    .iterator()
                )
                count = 0
                for row in rows:
                    writer.writerow([_serialize(value, timezone) for value in row])
                    count += 1
        except OSError as error:
            raise DataExportError(f'{path}: unable to write export: {error}') from error
        results.append((target, count))
    return results
