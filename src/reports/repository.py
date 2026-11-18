from django.db.models import Q

from src.loans.models import Loan


class DjangoMonthlyReportRepository:
    def for_period(self, start_on, end_before):
        started = Q(lent_on__gte=start_on, lent_on__lt=end_before)
        returned = Q(returned_on__gte=start_on, returned_on__lt=end_before)
        return Loan.objects.filter(started | returned)
