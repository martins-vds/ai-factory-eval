from django.db import transaction

from src.loans.models import Loan


class LoanRepository:
    @staticmethod
    def all():
        return list(Loan.objects.order_by('id'))

    @staticmethod
    def find(loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    @staticmethod
    @transaction.atomic
    def save(loan):
        loan.save()
        return loan
