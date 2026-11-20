from django.db import transaction

from .models import Loan


class LoanRepository:
    def all(self):
        return Loan.objects.all()

    def count(self):
        return Loan.objects.count()

    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    @transaction.atomic
    def create(self, **fields):
        return Loan.objects.create(**fields)

    @transaction.atomic
    def return_if_unreturned(self, loan_id, returned_on):
        updated = Loan.objects.filter(pk=loan_id, returned_on__isnull=True).update(returned_on=returned_on)
        return self.find(loan_id) if updated else None
