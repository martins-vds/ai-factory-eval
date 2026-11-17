from django.db import transaction

from src.loans.models import Loan


class LoanRepository:
    def list(self):
        return Loan.objects.all()

    def get(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    @transaction.atomic
    def create(self, **fields):
        return Loan.objects.create(**fields)
