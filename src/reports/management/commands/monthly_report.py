import csv
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.reports.composition import monthly_report


class Command(BaseCommand):
    help = 'Print the previous month lending report as CSV.'

    def handle(self, *args, **options):
        current_month_starts = timezone.localdate().replace(day=1)
        previous_month_ends = current_month_starts
        previous_month_starts = (current_month_starts - timedelta(days=1)).replace(day=1)
        rows = monthly_report.generate(previous_month_starts, previous_month_ends)

        writer = csv.writer(self.stdout)
        writer.writerow(
            [
                'member_id',
                'loans_started',
                'loans_returned_late',
                'total_late_fees_cents',
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.member_id,
                    row.loans_started,
                    row.loans_returned_late,
                    row.total_late_fees_cents,
                ]
            )
