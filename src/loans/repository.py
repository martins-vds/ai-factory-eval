from .models import Loan


class LoanRepository:
    @staticmethod
    def list_all():
        return Loan.objects.order_by('id')

    @staticmethod
    def find_by_id(loan_id):
        return Loan.objects.filter(pk=loan_id).first()
