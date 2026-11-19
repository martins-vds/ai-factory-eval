import csv

from django.core.management.base import BaseCommand

from src.reports.composition import monthly_report_application


class Command(BaseCommand):
    help = 'Write the previous calendar month lending report as CSV.'

    def handle(self, *args, **options):
        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        for row in monthly_report_application.generate():
            writer.writerow(
                [row.member_id, row.loans_started, row.late_returns, row.late_fees_cents]
            )
