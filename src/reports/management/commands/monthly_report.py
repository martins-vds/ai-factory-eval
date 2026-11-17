import csv

from django.core.management.base import BaseCommand

from src.reports.composition import monthly_report_application


class Command(BaseCommand):
    def handle(self, *args, **options):
        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member', 'loans_started', 'late_returns', 'late_fees_cents'])
        for row in monthly_report_application.generate():
            writer.writerow([row.member, row.loans_started, row.late_returns, row.late_fees_cents])
