import csv
import datetime
from pathlib import Path

import yaml
from django.core.management.base import BaseCommand, CommandError

from cargotracker.data_migration.loader import (
    DataLoadError,
    _mapping_timezone,
    _model_index,
    _prepare_tables,
)


def _format_value(value, timezone):
    if value is None:
        return r'\N'
    if isinstance(value, datetime.datetime):
        if value.utcoffset() is None:
            value = value.replace(tzinfo=timezone)
        return value.astimezone(datetime.UTC).isoformat().replace('+00:00', 'Z')
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
        raise DataLoadError(f'{mapping_file}: unable to read mapping: {error}') from error
    if not isinstance(mapping, dict):
        raise DataLoadError(f'{mapping_file}: mapping must be an object')

    timezone = _mapping_timezone(mapping)
    prepared = _prepare_tables(mapping, _model_index())
    output_directory = Path(output_path)
    try:
        output_directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise DataLoadError(
            f'{output_directory}: unable to create output directory: {error}'
        ) from error

    exported = []
    for entry in prepared:
        columns = entry['columns']
        fields = entry['fields']
        model = entry['model']
        target = entry['spec']['target']
        output_file = output_directory / f'{target}.csv'
        field_names = [fields[column].attname for column, _, _ in columns]
        try:
            with output_file.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow([column for column, _, _ in columns])
                rows = model._base_manager.order_by(model._meta.pk.name).values_list(*field_names)
                count = 0
                for row in rows:
                    writer.writerow(_format_value(value, timezone) for value in row)
                    count += 1
        except OSError as error:
            raise DataLoadError(f'{output_file}: unable to write export: {error}') from error
        exported.append((target, count))
    return exported


class Command(BaseCommand):
    help = 'Export mapped target tables as a relational snapshot.'

    def add_arguments(self, parser):
        parser.add_argument('--mapping', required=True)
        parser.add_argument('--out', required=True)

    def handle(self, *args, **options):
        try:
            exported = export_snapshot(options['mapping'], options['out'])
        except DataLoadError as error:
            raise CommandError(str(error)) from error
        total = sum(rows for _, rows in exported)
        self.stdout.write(
            self.style.SUCCESS(f'Exported {total} rows across {len(exported)} mapped tables.')
        )
