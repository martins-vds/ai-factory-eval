from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LateFee:
    late_days: int
    amount_cents: int

    @property
    def amount(self):
        return f'${self.amount_cents // 100}.{self.amount_cents % 100:02d}'


def calculate_late_fee(loan, today: date) -> LateFee:
    end_date = loan.returned_on or today
    late_days = max(0, (end_date - loan.due_on).days)
    amount_cents = 0 if late_days <= 2 else min(1000, late_days * 25)
    return LateFee(late_days, amount_cents)


class FeeApplication:
    def __init__(self, repository, clock):
        self.repository = repository
        self.clock = clock

    def get(self, loan_id):
        loan = self.repository.find(loan_id)
        if loan is None:
            return None
        return loan, calculate_late_fee(loan, self.clock.today())

    def all(self):
        today = self.clock.today()
        return [
            (loan, calculate_late_fee(loan, today))
            for loan in self.repository.all()
        ]
