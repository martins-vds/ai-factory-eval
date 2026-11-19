from django.db import transaction
from django.db.utils import IntegrityError

from .models import Loan


class LoanRepository:
    def all(self):
        return Loan.objects.all()

    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    @transaction.atomic
    def create(self, member, isbn, lent_on):
        while True:
            loan_ids = list(Loan.objects.select_for_update().values_list('pk', flat=True))
            loan_number = len(loan_ids) + 1
            while Loan.objects.filter(pk=f'L{loan_number}').exists():
                loan_number += 1
            loan_id = f'L{loan_number}'
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
        updated = Loan.objects.filter(pk=loan_id, returned_on__isnull=True).update(
            returned_on=returned_on
        )
        return self.find(loan_id) if updated else None
