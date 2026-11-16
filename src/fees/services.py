from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LateFee:
    late_days: int
    amount_cents: int

    @property
    def amount(self):
        return f'${self.amount_cents // 100}.{self.amount_cents % 100:02d}'


def calculate_late_fee(loan, *, today: date) -> LateFee:
    charged_through = loan.returned_on or today
    late_days = max(0, (charged_through - loan.due_on).days)
    amount_cents = 0 if late_days <= 2 else min(late_days * 25, 1000)
    return LateFee(late_days=late_days, amount_cents=amount_cents)
