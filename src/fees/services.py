from dataclasses import dataclass
from datetime import date
from decimal import Decimal
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
    loan: Loan
    days_late: int
    amount: Decimal


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def for_loan(self, loan_id: str) -> LateFee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        amount_cents = min(max(days_late - 2, 0) * 25, 1000)
        return LateFee(loan, days_late, Decimal(amount_cents) / 100)
