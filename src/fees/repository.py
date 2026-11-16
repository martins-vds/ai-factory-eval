from src.loans.models import Loan

from .services import FeeLoan


class DjangoFeeLoanRepository:
    def find(self, loan_id):
        loan = Loan.objects.filter(pk=loan_id).first()
        if loan is None:
            return None
        return FeeLoan(loan.id, loan.due_on, loan.returned_on)
