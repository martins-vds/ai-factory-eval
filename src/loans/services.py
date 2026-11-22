from datetime import date
from typing import Protocol


class Clock(Protocol):
    def today(self) -> date: ...


class LoanRepositoryPort(Protocol):
    def lend(self, member: str, isbn: str, lent_on: date): ...

    def find(self, loan_id: str): ...

    def mark_returned(self, loan_id: str, returned_on: date): ...


class InvalidLoan(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('Loan fields are invalid')


class LoanNotFound(Exception):
    pass


class LoanAlreadyReturned(Exception):
    def __init__(self, loan=None):
        self.loan = loan
        super().__init__('Loan has already been returned')


class LendBook:
    def __init__(self, repository: LoanRepositoryPort, clock: Clock):
        self._repository = repository
        self._clock = clock

    def execute(self, member: str | None, isbn: str | None):
        errors = {}
        if member is None or not member.strip():
            errors['member'] = 'Enter a member name; blank values are not accepted.'
        if isbn is None or not isbn.strip():
            errors['isbn'] = 'Enter an ISBN; blank values are not accepted.'
        if errors:
            raise InvalidLoan(errors)
        return self._repository.lend(member, isbn, self._clock.today())


class ReturnBook:
    def __init__(self, repository: LoanRepositoryPort, clock: Clock):
        self._repository = repository
        self._clock = clock

    def execute(self, loan_id: str):
        loan = self._repository.find(loan_id)
        if loan is None:
            raise LoanNotFound
        if loan.returned_on is not None:
            raise LoanAlreadyReturned(loan)
        loan = self._repository.mark_returned(loan_id, self._clock.today())
        if loan is None:
            raise LoanAlreadyReturned
        return loan
