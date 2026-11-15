import csv
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from src.reports.services import monthly_report


def parse_month(value: str) -> date:
    try:
        month_start = date.fromisoformat(f'{value}-01')
    except ValueError as exc:
        raise CommandError('month must be in YYYY-MM format') from exc
    if len(value) != 7:
        raise CommandError('month must be in YYYY-MM format')
    return month_start


class Command(BaseCommand):
    help = 'Write the monthly lending report as CSV.'

    def add_arguments(self, parser):
        parser.add_argument('--month', help='Report month in YYYY-MM format.')

    def handle(self, *args, **options):
        month_start = (
            parse_month(options['month'])
            if options['month']
            else (timezone.localdate().replace(day=1) - timedelta(days=1)).replace(day=1)
        )
        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        for row in monthly_report(month_start):
            writer.writerow(
                [row.member_id, row.loans_started, row.late_returns, row.late_fees_cents]
            )
