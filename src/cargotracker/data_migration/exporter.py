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
    path = Path(mapping_path)
    try:
        mapping = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{path}: unable to read mapping: {error}') from error
    if not isinstance(mapping, dict):
        raise DataExportError(f'{path}: mapping must be an object')
    specs = mapping.get('tables')
    if not isinstance(specs, list) or not specs:
        raise DataExportError('mapping has no tables')
    targets = [spec.get('target') if isinstance(spec, dict) else None for spec in specs]
    if (
        any(
            not isinstance(target, str)
            or target in ('.', '..')
            or '\\' in target
            or Path(target).name != target
            for target in targets
        )
        or len(targets) != len(set(targets))
    ):
        raise DataExportError('mapping targets must be unique table names')
    return mapping, specs


def _prepare_tables(specs):
    models = {
        model._meta.db_table: model
        for model in apps.get_models()
        if not model._meta.proxy and not model._meta.auto_created
    }
    prepared = []
    for spec in specs:
        target = spec['target']
        model = models.get(target)
        if model is None:
            raise DataExportError(f'{target}: no registered Django model for target table')
        columns = spec.get('columns')
        if not isinstance(columns, dict) or not columns:
            raise DataExportError(f'{target}: mapping has no columns')
        if any(not isinstance(name, str) for name in columns):
            raise DataExportError(f'{target}: mapped column names must be strings')
        fields = []
        for name in columns:
            field = next(
                (
                    candidate
                    for candidate in model._meta.concrete_fields
                    if name
                    in (candidate.column, candidate.name, candidate.attname)
                ),
                None,
            )
            if field is None:
                raise DataExportError(f'{target}: no target column {name!r}')
            fields.append(field)
        if model._meta.pk not in fields:
            raise DataExportError(f'{target}: mapping must include its primary key')
        prepared.append((target, model, fields))
    return prepared


def _mapping_timezone(mapping):
    defaults = mapping.get('defaults') or {}
    if not isinstance(defaults, dict):
        raise DataExportError('mapping defaults must be an object')
    zone = defaults.get('timestamp_tz', 'UTC')
    try:
        return ZoneInfo(zone)
    except (TypeError, ZoneInfoNotFoundError) as error:
        raise DataExportError(f'unknown timestamp timezone {zone!r}') from error


def _serialize(value, timezone):
    if value is None:
        return NULL_MARKER
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, datetime.date):
        return value.isoformat()
    return str(value)


def export_snapshot(mapping_path, output_path):
    mapping, specs = _read_mapping(mapping_path)
    tables = _prepare_tables(specs)
    timezone = _mapping_timezone(mapping)
    output = Path(output_path)
    exported = []
    try:
        output.mkdir(parents=True, exist_ok=True)
        for (target, model, fields), spec in zip(tables, specs, strict=True):
            path = output / f'{target}.csv'
            queryset = model._base_manager.order_by(model._meta.pk.name).values_list(
                *(field.attname for field in fields)
            )
            count = 0
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(spec['columns'])
                for row in queryset.iterator(chunk_size=1000):
                    writer.writerow([_serialize(value, timezone) for value in row])
                    count += 1
            exported.append((target, count))
    except OSError as error:
        raise DataExportError(f'{output}: unable to write export: {error}') from error
    return exported
