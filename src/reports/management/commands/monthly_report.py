import csv

from django.core.management.base import BaseCommand

from src.fees.composition import fee_application
from src.loans.clock import SystemClock
from src.reports.repository import DjangoMonthlyReportRepository
from src.reports.services import MonthlyReportApplication


class Command(BaseCommand):
    help = 'Print the previous calendar month lending report as CSV.'

    def handle(self, *args, **options):
        report = MonthlyReportApplication(
            DjangoMonthlyReportRepository(),
            SystemClock(),
            fee_application,
        )
        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        for row in report.rows():
            writer.writerow(
                [row.member_id, row.loans_started, row.late_returns, row.late_fees_cents]
            )
