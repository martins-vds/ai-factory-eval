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


class LoanNotFound(LookupError):
    pass


@dataclass(frozen=True)
class FeeQuote:
    loan_id: str
    due_on: date
    days_late: int
    amount: Decimal


class LateFeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate(self, loan_id: str) -> FeeQuote:
        loan = self.repository.find(loan_id)
        if loan is None:
            raise LoanNotFound(loan_id)

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        amount = (
            Decimal('0.00')
            if days_late <= 2
            else min(Decimal(days_late) * Decimal('0.25'), Decimal('10.00'))
        )
        return FeeQuote(loan.id, loan.due_on, days_late, amount)
