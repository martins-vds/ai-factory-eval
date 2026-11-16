from src.loans.models import Loan


class LoanRepository:
    def all(self):
        return list(Loan.objects.order_by('pk'))

    def get(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()
