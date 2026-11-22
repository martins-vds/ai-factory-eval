from django.db import transaction

from .domain import Loan as LoanRecord
from .domain import LoanAlreadyReturned
from .models import Loan as LoanModel


class LoanRepository:
    def all(self):
        return [self._record(loan) for loan in LoanModel.objects.all()]

    def find(self, loan_id):
        loan = LoanModel.objects.filter(pk=loan_id).first()
        return self._record(loan) if loan else None

    @transaction.atomic
    def lend(self, member, isbn, lent_on):
        LoanModel.objects.select_for_update().order_by('id').first()
        record = LoanModel.objects.create(
            id=f'L{LoanModel.objects.count() + 1}',
            member=member,
            isbn=isbn,
            lent_on=lent_on,
        )
        return self._record(record)

    @transaction.atomic
    def create(self, **fields):
        return LoanModel.objects.create(**fields)

    @transaction.atomic
    def save_returned(self, loan):
        record = LoanModel.objects.select_for_update().get(pk=loan.id)
        if record.returned_on is not None:
            raise LoanAlreadyReturned
        record.returned_on = loan.returned_on
        record.save(update_fields=['returned_on'])
        return self._record(record)

    @staticmethod
    def _record(loan):
        return LoanRecord(
            id=loan.id,
            member=loan.member,
            isbn=loan.isbn,
            lent_on=loan.lent_on,
            returned_on=loan.returned_on,
        )
