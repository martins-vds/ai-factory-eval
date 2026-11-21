from django.db.models import Q

from src.loans.models import Loan


class DjangoReportRepository:
    def for_period(self, start, end):
        return Loan.objects.filter(
            Q(lent_on__gte=start, lent_on__lt=end) | Q(returned_on__gte=start, returned_on__lt=end)
        )
