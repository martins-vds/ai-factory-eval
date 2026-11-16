import csv

from django.core.management.base import BaseCommand, CommandError

from src.reports.services import build_monthly_report, month_bounds


class Command(BaseCommand):
    help = 'Write the previous month lending report as CSV.'

    def add_arguments(self, parser):
        parser.add_argument('--month', help='Report month in YYYY-MM format.')

    def handle(self, *args, month=None, **options):
        try:
            start, end = month_bounds(month)
        except ValueError as error:
            raise CommandError('month must use YYYY-MM format') from error

        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        for row in build_monthly_report(start, end):
            writer.writerow(
                [row.member_id, row.loans_started, row.late_returns, row.late_fees_cents]
            )
