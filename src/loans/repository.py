from django.db import transaction

from .models import Loan


class LoanRepository:
    def all(self):
        return Loan.objects.all()

    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    @transaction.atomic
    def create(self, **fields):
        return Loan.objects.create(**fields)

    @transaction.atomic
    def lend(self, member, isbn, on):
        loan_id = f'L{Loan.objects.count() + 1}'
        return self.create(id=loan_id, member=member, isbn=isbn, lent_on=on)

    @transaction.atomic
    def mark_returned(self, loan_id, on):
        loan = Loan.objects.select_for_update().filter(pk=loan_id).first()
        if loan is None or loan.returned_on is not None:
            return None
        loan.returned_on = on
        loan.save(update_fields=['returned_on'])
        return loan
