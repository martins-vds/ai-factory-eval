import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.loans.models import Loan


@dataclass
class MemberTotals:
    loans_started: int = 0
    late_returns: int = 0
    total_late_fees_cents: int = 0


class Command(BaseCommand):
    help = 'Print the previous month lending report.'

    def handle(self, *args, **options):
        report_date = timezone.localdate()
        report_end = report_date.replace(day=1)
        report_start = (report_end - timedelta(days=1)).replace(day=1)
        totals = defaultdict(MemberTotals)

        loans = Loan.objects.filter(lent_on__gte=report_start, lent_on__lt=report_end).only(
            'member', 'lent_on', 'returned_on'
        )
        for loan in loans:
            member_totals = totals[loan.member]
            member_totals.loans_started += 1

            due_on = loan.lent_on + timedelta(days=14)
            end_date = loan.returned_on or report_date
            days_late = max(0, (end_date - due_on).days)
            if loan.returned_on is not None and days_late > 0:
                member_totals.late_returns += 1
            if days_late > 2:
                member_totals.total_late_fees_cents += min(1000, days_late * 25)

        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'total_late_fees_cents'])
        for member_id, member_totals in sorted(
            totals.items(), key=lambda item: (-item[1].total_late_fees_cents, item[0])
        ):
            writer.writerow(
                [
                    member_id,
                    member_totals.loans_started,
                    member_totals.late_returns,
                    member_totals.total_late_fees_cents,
                ]
            )
