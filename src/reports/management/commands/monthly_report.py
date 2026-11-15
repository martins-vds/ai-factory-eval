import csv
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.reports.repository import DjangoMonthlyReportRepository
from src.reports.services import MonthlyReportApplication


class Command(BaseCommand):
    help = 'Write the previous month lending report as CSV.'

    def handle(self, *args, **options):
        as_of = timezone.localdate()
        end = as_of.replace(day=1)
        start = (end - timedelta(days=1)).replace(day=1)
        rows = MonthlyReportApplication(DjangoMonthlyReportRepository()).for_month(
            start,
            end,
            as_of,
        )

        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'loans_returned_late', 'late_fees_cents'])
        writer.writerows(
            [
                row.member_id,
                row.loans_started,
                row.loans_returned_late,
                row.late_fees_cents,
            ]
            for row in rows
        )
