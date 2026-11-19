from src.loans.models import Loan


class DjangoReportLoanRepository:
    def __init__(self):
        self._period_loans = {}

    def for_period(self, start, end):
        loans = list(Loan.objects.filter(lent_on__gte=start, lent_on__lt=end))
        self._period_loans = {loan.id: loan for loan in loans}
        return loans

    def find(self, loan_id):
        return self._period_loans.get(loan_id)
