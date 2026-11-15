import csv

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.reports.services import monthly_report, previous_month_window


class Command(BaseCommand):
    help = 'Write the previous month lending report as CSV.'

    def handle(self, *args, **options):
        today = timezone.localdate()
        month_start, month_end = previous_month_window(today)
        writer = csv.writer(self.stdout)
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        for report in monthly_report(month_start, month_end, today):
            writer.writerow(
                [
                    report.member_id,
                    report.loans_started,
                    report.late_returns,
                    report.late_fees_cents,
                ]
            )
