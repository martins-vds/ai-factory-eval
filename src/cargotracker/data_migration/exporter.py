import csv
import datetime
from pathlib import Path

import yaml

from cargotracker.data_migration.loader import DataLoadError, _model_index, _prepare_tables

NULL_MARKER = r'\N'


class DataExportError(Exception):
    pass


def _read_mapping(path):
    try:
        mapping = yaml.safe_load(path.read_text(encoding='utf-8'))
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{path}: unable to read mapping: {error}') from error
    if mapping is None:
        mapping = {}
    if not isinstance(mapping, dict):
        raise DataExportError(f'{path}: mapping must be an object')
    return mapping


def _serialize(value):
    if value is None:
        return NULL_MARKER
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.UTC)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    return value


def export_snapshot(mapping_path, output_path):
    mapping_file = Path(mapping_path)
    mapping = _read_mapping(mapping_file)
    try:
        tables = _prepare_tables(mapping, _model_index())
    except DataLoadError as error:
        raise DataExportError(str(error)) from error

    output = Path(output_path)
    output.mkdir(parents=True, exist_ok=True)
    for entry in tables:
        spec = entry['spec']
        model = entry['model']
        columns = entry['columns']
        fields = entry['fields']
        primary_key = model._meta.pk
        values = [fields[target_column].attname for target_column, _, _ in columns]
        path = output / f'{spec["target"]}.csv'
        try:
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow([target_column for target_column, _, _ in columns])
                rows = model._base_manager.order_by(primary_key.name).values_list(*values)
                writer.writerows(
                    [_serialize(value) for value in row] for row in rows.iterator(chunk_size=1000)
                )
        except OSError as error:
            raise DataExportError(f'{path}: unable to write export: {error}') from error

    return len(tables)
