import csv
from io import StringIO

from src.loans.domain import Loan
from src.loans.ports import LoanRepository


class LoanNotFound(Exception):
    pass


class ListLoans:
    def __init__(self, repository: LoanRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Loan]:
        return sorted(self._repository.list_all(), key=lambda loan: loan.id)


class GetLoan:
    def __init__(self, repository: LoanRepository) -> None:
        self._repository = repository

    def execute(self, loan_id: str) -> Loan:
        loan = self._repository.get(loan_id)
        if loan is None:
            raise LoanNotFound(loan_id)
        return loan


class SaveLoan:
    def __init__(self, repository: LoanRepository) -> None:
        self._repository = repository

    def execute(self, loan: Loan) -> Loan:
        return self._repository.save(loan)


class ExportLoans:
    def __init__(self, repository: LoanRepository) -> None:
        self._repository = repository

    def execute(self, loans: list[Loan] | None = None) -> str:
        records = loans if loans is not None else ListLoans(self._repository).execute()
        output = StringIO(newline='')
        writer = csv.writer(output, delimiter=';', lineterminator='\n')
        for loan in records:
            writer.writerow(
                [
                    loan.id,
                    loan.member,
                    loan.isbn,
                    loan.lent_on.isoformat(),
                    loan.due_on.isoformat(),
                    loan.returned_on.isoformat() if loan.returned_on else '',
                ]
            )
        return output.getvalue()
