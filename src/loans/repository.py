from django.db import transaction

from src.loans.domain import Loan
from src.loans.models import LoanRecord


class DjangoLoanRepository:
    def list_loans(self) -> list[Loan]:
        return [_to_domain(record) for record in LoanRecord.objects.order_by('id')]

    def get_loan(self, loan_id: str) -> Loan | None:
        try:
            record = LoanRecord.objects.get(id=loan_id)
        except LoanRecord.DoesNotExist:
            return None
        return _to_domain(record)

    def add_loan(self, loan: Loan) -> Loan:
        with transaction.atomic():
            record = LoanRecord.objects.create(
                id=loan.loan_id,
                member=loan.member,
                isbn=loan.isbn,
                lent_on=loan.lent_on,
                returned_on=loan.returned_on,
            )
        return _to_domain(record)


def _to_domain(record: LoanRecord) -> Loan:
    return Loan(
        loan_id=record.id,
        member=record.member,
        isbn=record.isbn,
        lent_on=record.lent_on,
        returned_on=record.returned_on,
    )
