from django.db.models import Q

from src.loans.models import Loan


class DjangoReportLoanRepository:
    def for_period(self, start_on, end_on):
        return Loan.objects.filter(
            Q(lent_on__gte=start_on, lent_on__lt=end_on)
            | Q(returned_on__gte=start_on, returned_on__lt=end_on)
        ).order_by('id')
