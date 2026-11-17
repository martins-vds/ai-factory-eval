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
    days_late: int
    cents: int

    @property
    def amount(self):
        return f'${self.cents // 100}.{self.cents % 100:02d}'


def calculate_late_fee(loan: LoanRecord, today: date) -> LateFee:
    end_date = loan.returned_on or today
    days_late = max(0, (end_date - loan.due_on).days)
    cents = 0 if days_late <= 2 else min(1000, days_late * 25)
    return LateFee(days_late=days_late, cents=cents)


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def get_fee(self, loan_id: str) -> tuple[LoanRecord, LateFee] | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None
        return loan, calculate_late_fee(loan, self.clock.today())
