import csv
from pathlib import Path

import yaml

from cargotracker.data_migration.schema import (
    DataExportError,
    field_for_column,
    format_value,
    model_index,
    timestamp_timezone,
)


def _prepare_tables(mapping, models):
    specs = mapping.get('tables')
    if not isinstance(specs, list) or not specs:
        raise DataExportError('mapping has no tables')
    targets = [spec.get('target') if isinstance(spec, dict) else None for spec in specs]
    if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
        raise DataExportError('mapping targets must be unique table names')

    prepared = []
    for spec in specs:
        target = spec['target']
        model = models.get(target)
        if model is None:
            raise DataExportError(f'{target}: no registered Django model for target table')
        columns = spec.get('columns')
        if not isinstance(columns, dict) or not columns:
            raise DataExportError(f'{target}: mapping has no columns')
        fields = {column: field_for_column(model, column) for column in columns}
        key = spec.get('key')
        if not isinstance(key, list) or not key or any(column not in fields for column in key):
            raise DataExportError(f'{target}: mapping key must name mapped target columns')
        key_fields = [fields[column] for column in key]
        if model._meta.pk not in key_fields:
            raise DataExportError(f'{target}: mapping key must include the primary key')
        prepared.append(
            {
                'target': target,
                'model': model,
                'columns': list(columns),
                'fields': fields,
                'key_fields': key_fields,
            }
        )
    return prepared


def _write_table(output, table, timezone):
    path = output / f'{table["target"]}.csv'
    model = table['model']
    ordering = [model._meta.pk.name]
    try:
        with path.open('w', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream)
            writer.writerow(table['columns'])
            rows = model._base_manager.order_by(*ordering).iterator(chunk_size=1000)
            writer.writerows(
                [
                    format_value(getattr(row, table['fields'][column].attname), timezone)
                    for column in table['columns']
                ]
                for row in rows
            )
    except OSError as error:
        raise DataExportError(f'{path}: {error}') from error


def export_snapshot(mapping_path, output_path):
    mapping_file = Path(mapping_path)
    try:
        mapping = yaml.safe_load(mapping_file.read_text(encoding='utf-8'))
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{mapping_file}: unable to read mapping: {error}') from error
    if mapping is None:
        mapping = {}
    if not isinstance(mapping, dict):
        raise DataExportError(f'{mapping_file}: mapping must be an object')

    timezone = timestamp_timezone(mapping)
    tables = _prepare_tables(mapping, model_index())
    output = Path(output_path)
    try:
        output.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise DataExportError(f'{output}: {error}') from error
    for table in tables:
        _write_table(output, table, timezone)
    return [(table['target'], table['model']._base_manager.count()) for table in tables]
