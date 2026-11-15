import csv

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.reports.repository import DjangoMonthlyReportRepository
from src.reports.services import MonthlyReportService


class Command(BaseCommand):
    help = 'Write the previous month lending report as CSV.'

    def handle(self, *args, **options):
        rows = MonthlyReportService(DjangoMonthlyReportRepository()).for_previous_month(
            timezone.localdate()
        )
        writer = csv.writer(self.stdout)
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        writer.writerows(
            (
                row.member_id,
                row.loans_started,
                row.late_returns,
                row.late_fees_cents,
            )
            for row in rows
        )
