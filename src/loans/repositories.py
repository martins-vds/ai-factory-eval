from src.loans.models import Loan


class LoanRepository:
    def list(self):
        return Loan.objects.all()

    def get(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()
