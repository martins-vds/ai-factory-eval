from dataclasses import dataclass
from datetime import date

from src.loans.services import Clock, LoanRecord, LoanRepository


@dataclass(frozen=True)
class FeeQuote:
    loan: LoanRecord
    days_late: int
    amount_cents: int


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def quote(self, loan_id: str) -> FeeQuote | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        amount_cents = 0 if days_late <= 2 else min(days_late * 25, 1000)
        return FeeQuote(loan, days_late, amount_cents)
