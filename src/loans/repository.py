from django.db import transaction

from src.loans.models import Loan


class LoanRepository:
    @staticmethod
    def list_all():
        return Loan.objects.order_by('id')

    @staticmethod
    def get_by_id(loan_id):
        try:
            return Loan.objects.get(pk=loan_id)
        except Loan.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def save(loan):
        loan.save()
        return loan
