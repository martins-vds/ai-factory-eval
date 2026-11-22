from django.db import transaction

from src.loans.domain import Loan
from src.loans.models import LoanRecord


class DjangoLoanRepository:
    def all(self) -> list[Loan]:
        return [self._to_domain(record) for record in LoanRecord.objects.order_by('id')]

    def find(self, loan_id: str) -> Loan | None:
        record = LoanRecord.objects.filter(pk=loan_id).first()
        return self._to_domain(record) if record is not None else None

    @transaction.atomic
    def create(self, loan: Loan) -> Loan:
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
