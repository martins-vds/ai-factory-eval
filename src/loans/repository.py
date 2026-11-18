from django.db import transaction

from .models import Loan


class LoanRepository:
    def all(self):
        return Loan.objects.all()

    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    def next_id(self):
        return f'L{Loan.objects.count() + 1}'

    @transaction.atomic
    def create(self, **fields):
        return Loan.objects.create(**fields)

    @transaction.atomic
    def mark_returned(self, loan_id, returned_on):
        updated = Loan.objects.filter(pk=loan_id, returned_on__isnull=True).update(
            returned_on=returned_on
        )
        return self.find(loan_id) if updated else None
