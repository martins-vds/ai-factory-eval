from django.core.management.base import BaseCommand

from src.reports.composition import monthly_report


class Command(BaseCommand):
    help = 'Write the previous calendar month lending report as CSV.'

    def handle(self, *args, **options):
        self.stdout.write(monthly_report.render(), ending='')
