import csv
import datetime
from pathlib import Path

import yaml
from django.core.exceptions import ImproperlyConfigured

from cargotracker.data_migration.loader import (
    DataLoadError,
    _mapping_timezone,
    _model_index,
    _prepare_tables,
)


class DataExportError(Exception):
    pass


def _format_value(value, timezone):
    if value is None:
        return '\\N'
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, datetime.date):
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

    try:
        prepared = _prepare_tables(mapping, _model_index())
        timezone = _mapping_timezone(mapping)
    except (DataLoadError, ImproperlyConfigured) as error:
        raise DataExportError(str(error)) from error

    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
        row_counts = []
        for entry in prepared:
            spec = entry['spec']
            model = entry['model']
            columns = entry['columns']
            field_names = [entry['fields'][name].attname for name, _, _ in columns]
            row_count = 0
            with (output / f'{spec["target"]}.csv').open(
                'w',
                encoding='utf-8',
                newline='',
            ) as stream:
                writer = csv.writer(stream)
                writer.writerow([name for name, _, _ in columns])
                rows = (
                    model._base_manager.order_by(model._meta.pk.attname)
                    .values_list(*field_names)
                    .iterator()
                )
                for row in rows:
                    writer.writerow(_format_value(value, timezone) for value in row)
                    row_count += 1
            row_counts.append((spec['target'], row_count))
    except OSError as error:
        raise DataExportError(f'{output}: unable to write export: {error}') from error
    return row_counts
