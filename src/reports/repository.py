from src.loans.models import Loan


class DjangoReportLoanRepository:
    def __init__(self):
        self._loans = None

    def started_between(self, start, end):
        loans = list(Loan.objects.filter(lent_on__gte=start, lent_on__lt=end))
        self._loans = {loan.id: loan for loan in loans}
        return loans

    def find(self, loan_id):
        if self._loans is not None:
            return self._loans.get(loan_id)
        return Loan.objects.filter(pk=loan_id).first()
