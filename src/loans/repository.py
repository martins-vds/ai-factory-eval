from django.db import transaction

from .models import Loan


class LoanRepository:
    def atomic(self):
        return transaction.atomic()

    def all(self):
        return Loan.objects.all()

    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    def find_for_update(self, loan_id):
        return Loan.objects.select_for_update().filter(pk=loan_id).first()

    @transaction.atomic
    def create(self, **fields):
        return Loan.objects.create(**fields)

    def save(self, loan):
        loan.save(update_fields=['returned_on'])
        return loan
