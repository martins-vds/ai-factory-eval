from django.db import transaction

from src.loans.domain import Loan
from src.loans.models import LoanRecord


class DjangoLoanRepository:
    @transaction.atomic
    def list_all(self) -> list[Loan]:
        return [
            self._to_domain(record)
            for record in LoanRecord.objects.order_by('id')
        ]

    @transaction.atomic
    def find_by_id(self, loan_id: str) -> Loan | None:
        record = LoanRecord.objects.filter(pk=loan_id).first()
        return self._to_domain(record) if record is not None else None

    @transaction.atomic
    def save(self, loan: Loan) -> None:
        LoanRecord.objects.update_or_create(
            pk=loan.id,
            defaults={
                'member': loan.member,
                'isbn': loan.isbn,
                'lent_on': loan.lent_on,
                'returned_on': loan.returned_on,
            },
        )

    @staticmethod
    def _to_domain(record: LoanRecord) -> Loan:
        return Loan(
            id=record.id,
            member=record.member,
            isbn=record.isbn,
            lent_on=record.lent_on,
            returned_on=record.returned_on,
        )
