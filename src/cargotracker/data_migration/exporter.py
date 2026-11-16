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


def _format_value(value):
    if value is None:
        return r'\N'
    if isinstance(value, datetime.datetime):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=datetime.UTC)
        else:
            value = value.astimezone(datetime.UTC)
        return value.isoformat().replace('+00:00', 'Z')
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, bool):
        return str(value).lower()
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
        tables = _prepare_tables(mapping, _model_index())
    except DataLoadError as error:
        raise DataExportError(str(error)) from error

    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
        exported = []
        for entry in tables:
            spec = entry['spec']
            model = entry['model']
            columns = entry['columns']
            fields = [entry['fields'][target] for target, _, _ in columns]
            path = output / f'{spec["target"]}.csv'
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow([target for target, _, _ in columns])
                rows = model._base_manager.order_by(model._meta.pk.name).values_list(
                    *(field.attname for field in fields)
                )
                count = 0
                for row in rows:
                    writer.writerow([_format_value(value) for value in row])
                    count += 1
            exported.append((spec['target'], count))
    except OSError as error:
        raise DataExportError(f'{output}: unable to write export: {error}') from error
    return exported
