from django.core.management.base import BaseCommand, CommandError

from cargotracker.data_migration.exporter import DataExportError, export_snapshot


class Command(BaseCommand):
    help = 'Export mapped target tables as snapshot-format CSV files.'

    def add_arguments(self, parser):
        parser.add_argument('--mapping', required=True)
        parser.add_argument('--out', required=True)

    def handle(self, *args, **options):
        try:
            tables = export_snapshot(options['mapping'], options['out'])
        except DataExportError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(
            self.style.SUCCESS(f'Exported {tables} mapped tables to {options["out"]}.')
        )
