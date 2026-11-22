from django.db import transaction

from .domain import Loan
from .models import LoanRecord


class DjangoLoanRepository:
    def all(self) -> tuple[Loan, ...]:
        return tuple(self._to_domain(record) for record in LoanRecord.objects.order_by('id'))

    def find(self, loan_id: str) -> Loan | None:
        try:
            record = LoanRecord.objects.get(pk=loan_id)
        except LoanRecord.DoesNotExist:
            return None
        return self._to_domain(record)

    def create(self, loan: Loan) -> Loan:
        with transaction.atomic():
            record = LoanRecord.objects.create(
                id=loan.id,
                member=loan.member,
                isbn=loan.isbn,
                lent_on=loan.lent_on,
                returned_on=loan.returned_on,
            )
        return self._to_domain(record)

    @staticmethod
    def _to_domain(record: LoanRecord) -> Loan:
        return Loan(
            id=record.id,
            member=record.member,
            isbn=record.isbn,
            lent_on=record.lent_on,
            returned_on=record.returned_on,
        )
