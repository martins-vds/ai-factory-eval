from django.db import transaction

from .models import Loan


class LoanRepository:
    def all(self):
        return Loan.objects.all()

    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    def lend(self, member, isbn, lent_on):
        loan_id = f'L{Loan.objects.count() + 1}'
        return Loan.objects.create(
            id=loan_id,
            member=member,
            isbn=isbn,
            lent_on=lent_on,
        )

    def mark_returned(self, loan_id, returned_on):
        loan = self.find(loan_id)
        if loan is None:
            return None
        updated = Loan.objects.filter(
            pk=loan_id,
            returned_on__isnull=True,
        ).update(returned_on=returned_on)
        if updated:
            loan.returned_on = returned_on
            return loan, True
        loan.refresh_from_db(fields=['returned_on'])
        return loan, False

    @transaction.atomic
    def create(self, **fields):
        return Loan.objects.create(**fields)
