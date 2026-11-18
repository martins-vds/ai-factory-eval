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
    late_days: int
    amount_cents: int

    @property
    def formatted_amount(self) -> str:
        return f'{self.amount_cents // 100}.{self.amount_cents % 100:02d}'


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate(self, loan_id: str) -> LateFee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        late_days = max(0, ((loan.returned_on or self.clock.today()) - loan.due_on).days)
        amount_cents = 0 if late_days <= 2 else min(late_days * 25, 1000)
        return LateFee(loan.id, loan.due_on, late_days, amount_cents)
