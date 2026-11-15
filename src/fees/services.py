from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from src.loans.services import Clock, LoanRecord, LoanRepository


@dataclass(frozen=True)
class LateFee:
    days_late: int
    amount: Decimal


@dataclass(frozen=True)
class LoanFee:
    loan: LoanRecord
    days_late: int
    amount: Decimal


def calculate_late_fee(due_on: date, end_on: date) -> LateFee:
    days_late = max(0, (end_on - due_on).days)
    cents = 0 if days_late <= 2 else min(1000, days_late * 25)
    return LateFee(days_late, Decimal(cents) / 100)


class FeesApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def fee_for(self, loan_id: str) -> LoanFee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        fee = calculate_late_fee(loan.due_on, loan.returned_on or self.clock.today())
        return LoanFee(loan, fee.days_late, fee.amount)
