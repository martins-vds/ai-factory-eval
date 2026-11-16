import csv
import datetime
import hashlib
import json
from pathlib import Path

import yaml
from django.apps import apps

NULL_MARKER = '\\N'


class DataExportError(Exception):
    pass


def _read_mapping(path):
    try:
        with Path(path).open(encoding='utf-8') as stream:
            mapping = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as error:
        raise DataExportError(f'{path}: cannot read mapping: {error}') from error
    if not isinstance(mapping, dict) or not isinstance(mapping.get('tables'), list):
        raise DataExportError(f'{path}: mapping must contain a tables list')
    return mapping


def _model_index():
    return {
        model._meta.db_table: model
        for model in apps.get_models()
        if not model._meta.proxy and not model._meta.auto_created
    }


def _field_for_column(model, column):
    for field in model._meta.concrete_fields:
        if column in (field.column, field.name, field.attname):
            return field
    raise DataExportError(f'{model._meta.db_table}: no target column {column!r}')


def _serialize(value):
    if value is None:
        return NULL_MARKER
    if isinstance(value, datetime.datetime):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=datetime.UTC)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
    if isinstance(value, (datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def export_snapshot(mapping_path, output_dir):
    mapping = _read_mapping(mapping_path)
    tables = mapping['tables']
    targets = [table.get('target') if isinstance(table, dict) else None for table in tables]
    if (
        not tables
        or any(
            not isinstance(target, str)
            or not target
            or target in ('.', '..')
            or '/' in target
            or '\\' in target
            for target in targets
        )
        or len(targets) != len(set(targets))
    ):
        raise DataExportError('mapping targets must be unique table names')

    models = _model_index()
    output = Path(output_dir)
    exported = {}
    for table in tables:
        target = table['target']
        model = models.get(target)
        if model is None:
            raise DataExportError(f'{target}: no registered Django model for target table')
        columns = table.get('columns')
        if not isinstance(columns, dict) or not columns:
            raise DataExportError(f'{target}: mapping has no columns')
        fields = [_field_for_column(model, column) for column in columns]
        path = output / f'{target}.csv'
        output.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(columns)
            rows = model.objects.order_by(model._meta.pk.attname).values_list(
                *(field.attname for field in fields)
            )
            count = 0
            for row in rows.iterator():
                writer.writerow(_serialize(value) for value in row)
                count += 1
        exported[target] = {'rows': count, 'sha256': _sha256(path)}

    manifest_path = output / 'manifest.json'
    with manifest_path.open('w', encoding='utf-8', newline='') as stream:
        json.dump({'null': NULL_MARKER, 'tables': exported}, stream, indent=2)
        stream.write('\n')
    return exported
