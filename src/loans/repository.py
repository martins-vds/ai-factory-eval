from django.db import transaction

from src.loans.domain import Loan
from src.loans.models import LoanRecord


def _to_loan(record: LoanRecord) -> Loan:
    return Loan(
        id=record.id,
        member=record.member,
        isbn=record.isbn,
        lent_on=record.lent_on,
        returned_on=record.returned_on,
    )


class DjangoLoanRepository:
    def list_all(self) -> list[Loan]:
        return [_to_loan(record) for record in LoanRecord.objects.order_by('id')]

    def get(self, loan_id: str) -> Loan | None:
        record = LoanRecord.objects.filter(pk=loan_id).first()
        return _to_loan(record) if record is not None else None

    @transaction.atomic
    def save(self, loan: Loan) -> Loan:
        record = LoanRecord(
            id=loan.id,
            member=loan.member,
            isbn=loan.isbn,
            lent_on=loan.lent_on,
            returned_on=loan.returned_on,
        )
        record.save()
        return _to_loan(record)
