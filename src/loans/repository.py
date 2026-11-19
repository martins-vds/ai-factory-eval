from django.db import transaction

from .models import Loan


class LoanRepository:
    def all(self):
        return Loan.objects.all()

    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    @transaction.atomic
    def create(self, member, isbn, lent_on, id=None):
        loan_ids = list(Loan.objects.select_for_update().values_list('pk', flat=True))
        return Loan.objects.create(
            id=id or f'L{len(loan_ids) + 1}',
            member=member,
            isbn=isbn,
            lent_on=lent_on,
        )

    @transaction.atomic
    def mark_returned(self, loan_id, returned_on):
        updated = Loan.objects.filter(pk=loan_id, returned_on__isnull=True).update(
            returned_on=returned_on
        )
        return self.find(loan_id) if updated else None
