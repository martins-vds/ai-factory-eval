import csv
from collections import defaultdict
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.loans.models import Loan


class Command(BaseCommand):
    help = 'Print the previous month lending report.'

    def handle(self, *args, **options):
        report_date = timezone.localdate()
        report_end = report_date.replace(day=1)
        report_start = (report_end - timedelta(days=1)).replace(day=1)
        totals = defaultdict(lambda: [0, 0, 0])

        loans = Loan.objects.filter(lent_on__gte=report_start, lent_on__lt=report_end).only(
            'member', 'lent_on', 'returned_on'
        )
        for loan in loans:
            member_totals = totals[loan.member]
            member_totals[0] += 1

            due_on = loan.lent_on + timedelta(days=14)
            end_date = loan.returned_on or report_date
            days_late = max(0, (end_date - due_on).days)
            if loan.returned_on is not None and days_late > 0:
                member_totals[1] += 1
            if days_late > 2:
                member_totals[2] += min(1000, days_late * 25)

        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'total_late_fees_cents'])
        for member_id, (loans_started, late_returns, fees_cents) in sorted(
            totals.items(), key=lambda item: (-item[1][2], item[0])
        ):
            writer.writerow([member_id, loans_started, late_returns, fees_cents])
