from django.db import transaction

from .models import Loan


class LoanRepository:
    def all(self):
        return Loan.objects.all()

    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    @transaction.atomic
    def mark_returned(self, loan_id, returned_on):
        return (
            Loan.objects.filter(pk=loan_id, returned_on__isnull=True).update(returned_on=returned_on)
            == 1
        )

    @transaction.atomic
    def create(self, **fields):
        fields.setdefault('id', f'L{Loan.objects.count() + 1}')
        return Loan.objects.create(**fields)
