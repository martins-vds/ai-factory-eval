from django.db import IntegrityError, transaction

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
    def lend(self, member, isbn, lent_on):
        while True:
            loan_id = f'L{Loan.objects.count() + 1}'
            try:
                with transaction.atomic():
                    return Loan.objects.create(
                        id=loan_id,
                        member=member,
                        isbn=isbn,
                        lent_on=lent_on,
                    )
            except IntegrityError:
                if not Loan.objects.filter(pk=loan_id).exists():
                    raise

    @transaction.atomic
    def mark_returned(self, loan_id, returned_on):
        loan = Loan.objects.select_for_update().filter(pk=loan_id).first()
        if loan is None:
            return None
        if loan.returned_on is not None:
            return loan, False
        loan.returned_on = returned_on
        loan.save(update_fields=['returned_on'])
        return loan, True
