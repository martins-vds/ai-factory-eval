from src.loans.domain import Loan
from src.loans.models import LoanRecord


class DjangoLoanRepository:
    def list_all(self) -> list[Loan]:
        return [self._to_domain(record) for record in LoanRecord.objects.all()]

    def get(self, loan_id: str) -> Loan | None:
        record = LoanRecord.objects.filter(pk=loan_id).first()
        return self._to_domain(record) if record is not None else None

    @staticmethod
    def _to_domain(record: LoanRecord) -> Loan:
        return Loan(
            id=record.id,
            member=record.member,
            isbn=record.isbn,
            lent_on=record.lent_on,
            returned_on=record.returned_on,
        )
