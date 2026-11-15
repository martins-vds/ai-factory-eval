import csv
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

from src.loans.models import Loan


class Command(BaseCommand):
    help = 'Print the previous calendar month lending report as CSV.'

    def handle(self, *args, **options):
        month_end = timezone.localdate().replace(day=1)
        month_start = (month_end - timedelta(days=1)).replace(day=1)
        rows = {
            entry['member']: {
                'member_id': entry['member'],
                'loans_started': entry['loans_started'],
                'late_returns': 0,
                'late_fees_cents': 0,
            }
            for entry in (
                Loan.objects.filter(lent_on__gte=month_start, lent_on__lt=month_end)
                .values('member')
                .annotate(loans_started=Count('id'))
            )
        }

        late_loans = Loan.objects.filter(
            member__in=rows,
            returned_on__gte=month_start,
            returned_on__lt=month_end,
        ).only('member', 'lent_on', 'returned_on')
        for loan in late_loans:
            due_on = loan.lent_on + timedelta(days=14)
            days_late = (loan.returned_on - due_on).days
            if days_late <= 0:
                continue

            rows[loan.member]['late_returns'] += 1
            if days_late > 2:
                rows[loan.member]['late_fees_cents'] += min(1000, days_late * 25)

        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        for row in sorted(
            rows.values(), key=lambda item: (-item['late_fees_cents'], item['member_id'])
        ):
            writer.writerow(
                [
                    row['member_id'],
                    row['loans_started'],
                    row['late_returns'],
                    row['late_fees_cents'],
                ]
            )
