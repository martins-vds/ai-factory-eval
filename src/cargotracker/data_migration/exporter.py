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

NULL_MARKER = r'\N'


class DataExportError(Exception):
    pass


def _format_value(value, timestamp_timezone):
    if value is None:
        return NULL_MARKER
    if isinstance(value, datetime.datetime):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=timestamp_timezone)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, bool):
        return 'true' if value else 'false'
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
        timestamp_timezone = _mapping_timezone(mapping)
    except DataLoadError as error:
        raise DataExportError(str(error)) from error

    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
        exported = []
        for entry in prepared:
            spec = entry['spec']
            model = entry['model']
            columns = entry['columns']
            fields = [entry['fields'][target] for target, _, _ in columns]
            primary_key = getattr(model._meta.pk, 'fields', (model._meta.pk,))
            rows = (
                model._base_manager.order_by(*(field.name for field in primary_key))
                .values_list(*(field.attname for field in fields))
            )
            path = output / f'{spec["target"]}.csv'
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow([target for target, _, _ in columns])
                row_count = 0
                for row in rows.iterator():
                    writer.writerow(
                        [_format_value(value, timestamp_timezone) for value in row]
                    )
                    row_count += 1
            exported.append((spec['target'], row_count))
    except OSError as error:
        raise DataExportError(f'{output}: unable to write export: {error}') from error

    return exported
