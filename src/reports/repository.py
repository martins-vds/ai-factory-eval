from django.db.models import Q

from src.loans.models import Loan


class DjangoReportLoanRepository:
    def __init__(self):
        self._loans = {}

    def for_period(self, start_on, end_on):
        loans = list(
            Loan.objects.filter(
                Q(lent_on__gte=start_on, lent_on__lt=end_on)
                | Q(returned_on__gte=start_on, returned_on__lt=end_on)
            ).order_by('id')
        )
        self._loans = {loan.id: loan for loan in loans}
        return loans

    def find(self, loan_id):
        return self._loans.get(loan_id)
