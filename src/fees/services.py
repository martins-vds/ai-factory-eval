from dataclasses import dataclass
from datetime import date
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
class FeeQuote:
    loan: LoanRecord
    late_days: int
    amount_cents: int


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate_fee(self, loan_id: str) -> FeeQuote | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        late_days = max(0, (end_date - loan.due_on).days)
        amount_cents = 0 if late_days <= 2 else min(1000, late_days * 25)
        return FeeQuote(loan, late_days, amount_cents)
