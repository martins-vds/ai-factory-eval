from django.db.models import Q

from src.loans.models import Loan


class DjangoMonthlyReportRepository:
    def activity_between(self, start_on, end_on):
        return Loan.objects.filter(
            Q(lent_on__gte=start_on, lent_on__lt=end_on)
            | Q(returned_on__gte=start_on, returned_on__lt=end_on)
        ).only('member', 'lent_on', 'returned_on')
