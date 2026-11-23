import csv
import datetime
from pathlib import Path

import yaml

from cargotracker.data_migration.loader import (
    DataLoadError,
    _mapping_timezone,
    _model_index,
    _prepare_tables,
)


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


def _format_value(value, timestamp_timezone):
    if value is None:
        return r'\N'
    if isinstance(value, datetime.datetime):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=timestamp_timezone)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, datetime.date):
        return value.isoformat()
    return str(value)


def export_snapshot(mapping_path, output_path):
    mapping = _read_mapping(mapping_path)
    try:
        prepared = _prepare_tables(mapping, _model_index())
        timestamp_timezone = _mapping_timezone(mapping)
    except DataLoadError as error:
        raise DataExportError(str(error)) from error

    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
        row_counts = []
        for entry in prepared:
            spec = entry['spec']
            model = entry['model']
            columns = [target_column for target_column, _, _ in entry['columns']]
            fields = [entry['fields'][column] for column in columns]
            rows = model._base_manager.order_by(model._meta.pk.name).values_list(
                *(field.attname for field in fields)
            )
            path = output / f'{spec["target"]}.csv'
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                count = 0
                for row in rows:
                    writer.writerow([_format_value(value, timestamp_timezone) for value in row])
                    count += 1
            row_counts.append((spec['target'], count))
    except OSError as error:
        raise DataExportError(f'{output}: unable to write export: {error}') from error
    return row_counts
