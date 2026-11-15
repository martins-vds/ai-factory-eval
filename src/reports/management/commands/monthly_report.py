import csv
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.loans.models import Loan


def _next_month(month):
    return (month.replace(day=28) + timedelta(days=4)).replace(day=1)


class Command(BaseCommand):
    help = 'Write the monthly lending report as CSV.'

    def handle(self, *args, **options):
        today = timezone.localdate()
        month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        report_date = _next_month(month)
        loans = Loan.objects.filter(
            lent_on__gte=month,
            lent_on__lt=report_date,
        ).only('member', 'lent_on', 'returned_on')
        totals = {}

        for loan in loans:
            member = loan.member
            due_on = loan.due_on
            returned_on = loan.returned_on
            returned_by_report_date = returned_on is not None and returned_on <= report_date
            fee_end = returned_on if returned_by_report_date else report_date
            days_late = max(0, (fee_end - due_on).days)
            fee_cents = 0 if days_late <= 2 else min(1000, days_late * 25)
            member_totals = totals.setdefault(
                member,
                {'loans_started': 0, 'late_returns': 0, 'late_fees_cents': 0},
            )
            member_totals['loans_started'] += 1
            member_totals['late_fees_cents'] += fee_cents
            if returned_by_report_date and returned_on > due_on:
                member_totals['late_returns'] += 1

        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(['member_id', 'loans_started', 'late_returns', 'late_fees_cents'])
        for member, member_totals in sorted(
            totals.items(),
            key=lambda entry: (-entry[1]['late_fees_cents'], entry[0]),
        ):
            writer.writerow(
                [
                    member,
                    member_totals['loans_started'],
                    member_totals['late_returns'],
                    member_totals['late_fees_cents'],
                ]
            )
