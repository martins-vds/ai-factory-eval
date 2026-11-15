from datetime import date

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
    def lend(self, member, isbn):
        loan_id = f'L{Loan.objects.count() + 1}'
        return Loan.objects.create(
            id=loan_id,
            member=member,
            isbn=isbn,
            lent_on=date.today(),
        )
