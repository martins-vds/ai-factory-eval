from django.db import transaction

from .models import Loan
from .services import LoanAlreadyReturned, LoanNotFound


class LoanRepository:
    def all(self):
        return Loan.objects.all()

    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    @transaction.atomic
    def create(self, **fields):
        fields.setdefault('id', f'L{Loan.objects.count() + 1}')
        return Loan.objects.create(**fields)

    @transaction.atomic
    def mark_returned(self, loan_id, returned_on):
        loan = Loan.objects.select_for_update().filter(pk=loan_id).first()
        if loan is None:
            raise LoanNotFound(loan_id)
        if loan.returned_on is not None:
            raise LoanAlreadyReturned(loan_id)
        loan.returned_on = returned_on
        loan.save(update_fields=['returned_on'])
        return loan
