import csv
from collections.abc import Iterable
from datetime import date
from io import StringIO
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    isbn: str
    lent_on: date
    due_on: date
    returned_on: date | None


class Clock(Protocol):
    def today(self) -> date: ...


class LoanRepositoryPort(Protocol):
    def all(self) -> Iterable[LoanRecord]: ...

    def find(self, loan_id: str) -> LoanRecord | None: ...

    def create(self, **fields: object) -> LoanRecord: ...

    def next_id(self) -> str: ...


def lend_loan(repository: LoanRepositoryPort, clock: Clock, member: str, isbn: str) -> LoanRecord:
    return repository.create(
        id=repository.next_id(),
        member=member,
        isbn=isbn,
        lent_on=clock.today(),
    )


def loan_line(loan: LoanRecord) -> str:
    output = StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
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


def list_loans_text(repository: LoanRepositoryPort) -> str:
    return ''.join(loan_line(loan) for loan in repository.all())


def get_loan_text(repository: LoanRepositoryPort, loan_id: str) -> str | None:
    loan = repository.find(loan_id)
    return loan_line(loan) if loan else None
