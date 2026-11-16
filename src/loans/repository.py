from django.db import transaction

from .models import Loan


class LoanAlreadyReturned(Exception):
    pass


class LoanRepository:
    def all(self):
        return Loan.objects.all()

    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    @transaction.atomic
    def create(self, **fields):
        return Loan.objects.create(**fields)

    @transaction.atomic
    def lend(self, member, isbn, lent_on):
        loan_id = f'L{Loan.objects.count() + 1}'
        return Loan.objects.create(
            id=loan_id,
            member=member,
            isbn=isbn,
            lent_on=lent_on,
        )

    @transaction.atomic
    def mark_returned(self, loan_id, returned_on):
        loan = Loan.objects.select_for_update().filter(pk=loan_id).first()
        if loan is None:
            return None
        if loan.returned_on is not None:
            raise LoanAlreadyReturned
        loan.returned_on = returned_on
        loan.save(update_fields=['returned_on'])
        return loan
