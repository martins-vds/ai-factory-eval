import csv

from django.core.management.base import BaseCommand

from src.reports.composition import monthly_report_application


class Command(BaseCommand):
    def handle(self, *args, **options):
        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        for report in monthly_report_application.generate():
            writer.writerow(
                [
                    report.member_id,
                    report.loans_started,
                    report.late_returns,
                    report.late_fees_cents,
                ]
            )
