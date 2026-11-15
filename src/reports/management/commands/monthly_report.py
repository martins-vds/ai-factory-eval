import csv
from datetime import date
from io import StringIO

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.fees.composition import fee_application
from src.reports.repository import DjangoMonthlyReportRepository
from src.reports.services import MonthlyReport


class Command(BaseCommand):
    def handle(self, *args, **options):
        today = timezone.localdate()
        year, month = today.year, today.month - 1
        if month == 0:
            year, month = year - 1, 12

        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)

        output = StringIO()
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        for report in MonthlyReport(DjangoMonthlyReportRepository(), fee_application).for_period(start, end):
            writer.writerow(
                [
                    report.member_id,
                    report.loans_started,
                    report.late_returns,
                    report.late_fees_cents,
                ]
            )
        self.stdout.write(output.getvalue(), ending='')
