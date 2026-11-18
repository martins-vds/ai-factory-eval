from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def find(self, loan_id: str) -> LoanRecord | None: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass(frozen=True)
class LateFee:
    loan_id: str
    due_on: date
    late_days: int
    amount: Decimal


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate(self, loan_id: str) -> LateFee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        late_days = max(0, ((loan.returned_on or self.clock.today()) - loan.due_on).days)
        billable_days = max(0, late_days - 2)
        amount = min(Decimal('0.25') * billable_days, Decimal('10.00'))

        return LateFee(loan.id, loan.due_on, late_days, amount)
