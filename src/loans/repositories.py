from django.db import transaction

from src.loans.models import Loan


class LoanRepository:
    @staticmethod
    @transaction.atomic
    def save(loan):
        loan.save()
        return loan

    @staticmethod
    @transaction.atomic
    def all():
        return list(Loan.objects.order_by('id'))

    @staticmethod
    @transaction.atomic
    def find(loan_id):
        return Loan.objects.filter(pk=loan_id).first()
