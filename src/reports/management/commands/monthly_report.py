import csv

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.reports.monthly import previous_month_report


class Command(BaseCommand):
    help = 'Print the previous month lending report.'

    def handle(self, *args, **options):
        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        for row in previous_month_report(timezone.localdate()):
            writer.writerow(
                [row.member_id, row.loans_started, row.late_returns, row.late_fees_cents]
            )
