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
    def lend(self, *, member, isbn, lent_on):
        return Loan.objects.create(
            id=f'L{Loan.objects.count() + 1}',
            member=member,
            isbn=isbn,
            lent_on=lent_on,
        )
