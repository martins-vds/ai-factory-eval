import csv
from datetime import date

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.reports.services import monthly_report


def previous_month(today: date) -> tuple[date, date]:
    period_end = date(today.year, today.month, 1)
    if period_end.month == 1:
        period_start = date(period_end.year - 1, 12, 1)
    else:
        period_start = date(period_end.year, period_end.month - 1, 1)
    return period_start, period_end


class Command(BaseCommand):
    help = 'Print the monthly lending report for the previous calendar month.'

    def handle(self, *args, **options):
        period_start, period_end = previous_month(timezone.localdate())
        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member', 'loans_started', 'late_returns', 'late_fees_cents'])
        for row in monthly_report(period_start, period_end):
            writer.writerow(
                [row.member, row.loans_started, row.late_returns, row.late_fees_cents]
            )
