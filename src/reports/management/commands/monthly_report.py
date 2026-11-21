from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from src.loans.repository import DjangoLoanRepository
from src.reports.services import MonthlyReportApplication


class Command(BaseCommand):
    help = 'Produce the prior-month lending report.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            help='Month to report, in YYYY-MM format (defaults to the prior calendar month).',
        )

    def handle(self, *args, **options):
        month = options['month']
        if month:
            try:
                year_text, month_text = month.split('-')
                year, month_number = int(year_text), int(month_text)
                month_start = date(year, month_number, 1)
            except (TypeError, ValueError):
                raise CommandError('Month must use YYYY-MM format.') from None
        else:
            today = timezone.localdate()
            if today.month == 1:
                month_start = date(today.year - 1, 12, 1)
            else:
                month_start = date(today.year, today.month - 1, 1)

        if month_start.month == 12:
            month_end = date(month_start.year + 1, 1, 1)
        else:
            month_end = date(month_start.year, month_start.month + 1, 1)

        application = MonthlyReportApplication(DjangoLoanRepository())
        for row in application.report(month_start, month_end):
            self.stdout.write(
                f'{row.member},{row.loans_started},{row.late_returns},{row.late_fees_cents}'
            )
