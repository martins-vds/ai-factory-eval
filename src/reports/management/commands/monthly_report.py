import csv

from django.core.management.base import BaseCommand

from src.reports.clock import SystemClock
from src.reports.repository import DjangoReportLoanRepository
from src.reports.services import MonthlyReportApplication


class Command(BaseCommand):
    help = 'Write the previous month lending report as CSV.'

    def handle(self, *args, **options):
        report = MonthlyReportApplication(DjangoReportLoanRepository(), SystemClock()).run()
        writer = csv.writer(self.stdout)
        writer.writerow(
            ('member_id', 'loans_started', 'late_returns', 'total_late_fees_cents')
        )
        for row in report:
            writer.writerow(
                (row.member_id, row.loans_started, row.late_returns, row.total_late_fees_cents)
            )
