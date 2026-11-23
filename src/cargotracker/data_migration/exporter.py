import csv
import datetime
from pathlib import Path

import yaml

from cargotracker.data_migration.loader import (
    DataLoadError,
    _model_index,
    _prepare_tables,
)


class DataExportError(Exception):
    pass


def _serialize(value):
    if value is None:
        return r'\N'
    if isinstance(value, datetime.datetime):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=datetime.UTC)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, datetime.date):
        return value.isoformat()
    return str(value)


def export_snapshot(mapping_path, output_path):
    mapping_file = Path(mapping_path)
    output = Path(output_path)
    try:
        mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8')) or {}
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
    if not isinstance(mapping, dict):
        raise DataExportError(f'{mapping_file}: mapping must be an object')

    try:
        tables = _prepare_tables(mapping, _model_index())
    except DataLoadError as error:
        raise DataExportError(str(error)) from error

    try:
        output.mkdir(parents=True, exist_ok=True)
        row_counts = []
        for table in tables:
            target = table['spec']['target']
            columns = [target_column for target_column, _, _ in table['columns']]
            fields = [table['fields'][column] for column in columns]
            rows = (
                table['model']
                ._base_manager.order_by(table['model']._meta.pk.attname)
                .values_list(*(field.attname for field in fields))
            )
            path = output / f'{target}.csv'
            with path.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                row_count = 0
                for row in rows:
                    writer.writerow([_serialize(value) for value in row])
                    row_count += 1
            row_counts.append((target, row_count))
    except OSError as error:
        raise DataExportError(f'{output}: unable to write export: {error}') from error
    return row_counts
