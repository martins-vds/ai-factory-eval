import csv
from collections import defaultdict
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.loans.models import Loan


class Command(BaseCommand):
    help = 'Write a CSV summary of loans started in the previous month.'

    def handle(self, *args, **options):
        current_month_start = timezone.localdate().replace(day=1)
        report_end = current_month_start - timedelta(days=1)
        report_start = report_end.replace(day=1)
        members = defaultdict(lambda: [0, 0, 0])

        loans = Loan.objects.filter(
            lent_on__gte=report_start,
            lent_on__lte=report_end,
        )
        for loan in loans:
            totals = members[loan.member]
            totals[0] += 1
            assessment_date = min(loan.returned_on, report_end) if loan.returned_on else report_end
            days_late = max(0, (assessment_date - loan.due_on).days)
            if days_late > 2:
                totals[2] += min(1000, days_late * 25)
            if loan.returned_on and loan.due_on < loan.returned_on <= report_end:
                totals[1] += 1

        writer = csv.writer(self.stdout, lineterminator='\n')
        writer.writerow(('member_id', 'loans_started', 'late_returns', 'late_fees_cents'))
        for member, totals in sorted(members.items(), key=lambda item: (-item[1][2], item[0])):
            writer.writerow((member, *totals))
