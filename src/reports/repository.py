from django.db.models import Q

from src.loans.models import Loan


class DjangoMonthlyReportRepository:
    def loans_with_activity_between(self, starts_on, ends_before):
        return Loan.objects.filter(
            Q(lent_on__gte=starts_on, lent_on__lt=ends_before)
            | Q(returned_on__gte=starts_on, returned_on__lt=ends_before)
        )
