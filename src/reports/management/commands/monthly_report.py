import csv

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.reports.composition import monthly_report


class Command(BaseCommand):
    def handle(self, *args, **options):
        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(
            [
                'member_id',
                'loans_started',
                'late_returns',
                'total_late_fees_cents',
            ]
        )
        for row in monthly_report.for_previous_month(timezone.localdate()):
            writer.writerow(
                [
                    row.member_id,
                    row.loans_started,
                    row.late_returns,
                    row.total_late_fees_cents,
                ]
            )
