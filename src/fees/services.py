from dataclasses import dataclass
from datetime import date
from typing import Protocol


class LoanRecord(Protocol):
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def find(self, loan_id: str) -> LoanRecord | None: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass(frozen=True)
class LateFee:
    loan: LoanRecord
    days_late: int
    amount_cents: int


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate(self, loan_id: str) -> LateFee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        amount_cents = 0 if days_late <= 2 else min(1000, days_late * 25)
        return LateFee(loan, days_late, amount_cents)
