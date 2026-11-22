from dataclasses import dataclass
from datetime import date
from typing import Protocol


class Loan(Protocol):
    id: str
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def find(self, loan_id: str) -> Loan | None: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass(frozen=True)
class LateFee:
    loan_id: str
    due_on: date
    days_late: int
    amount_cents: int


class FeeApplication:
    def __init__(self, loans: LoanRepository, clock: Clock):
        self.loans = loans
        self.clock = clock

    def calculate(self, loan_id: str) -> LateFee | None:
        loan = self.loans.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        amount_cents = min(1000, days_late * 25) if days_late > 2 else 0
        return LateFee(loan.id, loan.due_on, days_late, amount_cents)
