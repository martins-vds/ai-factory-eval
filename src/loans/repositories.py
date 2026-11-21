from src.loans.models import Loan


class LoanRepository:
    def list(self):
        return list(Loan.objects.all().order_by('id'))

    def get(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()
