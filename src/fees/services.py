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
class LateFeeQuote:
    loan: LoanRecord
    days_late: int
    amount_cents: int

    @property
    def formatted_amount(self) -> str:
        return f'${self.amount_cents // 100}.{self.amount_cents % 100:02d}'


class FeeApplication:
    def __init__(self, loan_repository: LoanRepository, clock: Clock):
        self.loan_repository = loan_repository
        self.clock = clock

    def quote_for(self, loan_id: str) -> LateFeeQuote | None:
        loan = self.loan_repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        chargeable_days = max(0, days_late - 2)
        amount_cents = min(chargeable_days * 25, 1000)
        return LateFeeQuote(loan, days_late, amount_cents)
