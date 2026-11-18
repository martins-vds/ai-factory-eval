from django.core.management.base import BaseCommand

from src.reports.composition import monthly_report


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(monthly_report.generate(), ending='')
