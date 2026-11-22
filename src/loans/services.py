import csv
import io

from .domain import Loan
from .ports import LoanRepository


class LoanCatalog:
    def __init__(self, repository: LoanRepository) -> None:
        self._repository = repository

    def all(self) -> tuple[Loan, ...]:
        return tuple(self._repository.all())

    def get(self, loan_id: str) -> Loan | None:
        return self._repository.find(loan_id)

    def text_export(self) -> str:
        return ''.join(f'{self.text_line(loan)}\n' for loan in self.all())

    @staticmethod
    def text_line(loan: Loan) -> str:
        row = io.StringIO(newline='')
        csv.writer(row, delimiter=';', lineterminator='').writerow(
            (
                loan.id,
                loan.member,
                loan.isbn,
                loan.lent_on.isoformat(),
                loan.due_on.isoformat(),
                loan.returned_on.isoformat() if loan.returned_on else '',
            )
        )
        return row.getvalue()
