import csv
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.loans.models import Loan


class Command(BaseCommand):
    help = 'Print the monthly lending report for the previous calendar month.'

    def handle(self, *args, **options):
        as_of = timezone.localdate()
        month_end = as_of.replace(day=1)
        month_start = (month_end - timedelta(days=1)).replace(day=1)
        members = {}

        loans = Loan.objects.filter(lent_on__gte=month_start, lent_on__lt=month_end).values_list(
            'member', 'lent_on', 'returned_on'
        )
        for member, lent_on, returned_on in loans.iterator():
            due_on = lent_on + timedelta(days=14)
            fee_end = returned_on or as_of
            days_late = max(0, (fee_end - due_on).days)
            fee_cents = 0 if days_late <= 2 else min(1000, days_late * 25)
            row = members.setdefault(member, [0, 0, 0])
            row[0] += 1
            row[1] += int(returned_on is not None and returned_on > due_on)
            row[2] += fee_cents

        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(('member_id', 'loans_started', 'late_returns', 'late_fees_cents'))
        for member, (loans_started, late_returns, late_fees_cents) in sorted(
            members.items(), key=lambda item: (-item[1][2], item[0])
        ):
            writer.writerow((member, loans_started, late_returns, late_fees_cents))
