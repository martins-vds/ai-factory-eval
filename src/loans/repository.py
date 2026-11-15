from django.db import transaction
from django.utils import timezone

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
        next_id = Loan.objects.count() + 1
        while Loan.objects.filter(pk=f'L{next_id}').exists():
            next_id += 1
        return Loan.objects.create(
            id=f'L{next_id}',
            member=member,
            isbn=isbn,
            lent_on=timezone.localdate(),
        )

    @transaction.atomic
    def mark_returned(self, loan_id):
        loan = Loan.objects.select_for_update().filter(pk=loan_id).first()
        if loan is None:
            return None, False
        if loan.returned_on is not None:
            return loan, False
        loan.returned_on = timezone.localdate()
        loan.save(update_fields=['returned_on'])
        return loan, True
