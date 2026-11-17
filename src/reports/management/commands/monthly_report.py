from django.core.management.base import BaseCommand

from src.reports.services import monthly_report_rows, write_monthly_report


class Command(BaseCommand):
    help = 'Write the previous month lending report to standard output.'

    def handle(self, *args, **options):
        write_monthly_report(monthly_report_rows(), self.stdout)
