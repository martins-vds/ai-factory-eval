from src.loans.models import Loan


class DjangoFeeRepository:
    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()
