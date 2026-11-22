from src.loans.models import Loan


class DjangoReportLoanRepository:
    def __init__(self):
        self._loans_by_id = None

    def all(self):
        loans = list(Loan.objects.all())
        self._loans_by_id = {loan.id: loan for loan in loans}
        return loans

    def find(self, loan_id):
        if self._loans_by_id is not None:
            return self._loans_by_id.get(loan_id)
        return Loan.objects.filter(pk=loan_id).first()
