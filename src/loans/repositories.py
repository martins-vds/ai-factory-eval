from src.loans.models import Loan


class LoanRepository:
    def list(self):
        return Loan.objects.all()
