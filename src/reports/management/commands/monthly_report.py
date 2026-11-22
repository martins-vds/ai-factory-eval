import csv
from io import StringIO

from django.core.management.base import BaseCommand

from src.fees.gateway import HttpPaymentGateway
from src.fees.services import FeeApplication
from src.loans.clock import SystemClock
from src.reports.repository import DjangoReportLoanRepository
from src.reports.services import MonthlyReportApplication


class Command(BaseCommand):
    help = 'Write the previous month lending report as CSV.'

    def handle(self, *args, **options):
        loans = DjangoReportLoanRepository()
        clock = SystemClock()
        fees = FeeApplication(loans, clock, HttpPaymentGateway())
        report = MonthlyReportApplication(loans, clock, fees).generate()
        output = StringIO(newline='')
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(
            ['member_id', 'loans_started', 'loans_returned_late', 'total_late_fees_cents']
        )
        writer.writerows(
            [
                row.member_id,
                row.loans_started,
                row.loans_returned_late,
                row.total_late_fees_cents,
            ]
            for row in report
        )
        self.stdout.write(output.getvalue(), ending='')
