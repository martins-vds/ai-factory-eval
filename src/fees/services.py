from dataclasses import dataclass
from datetime import date

from django.utils import timezone


@dataclass(frozen=True)
class LateFee:
    days_late: int
    amount_cents: int

    @property
    def formatted_amount(self):
        return f'${self.amount_cents // 100}.{self.amount_cents % 100:02d}'


def calculate_late_fee(loan, *, today: date | None = None) -> LateFee:
    end_date = loan.returned_on or today or timezone.localdate()
    days_late = max(0, (end_date - loan.due_on).days)
    amount_cents = 0 if days_late <= 2 else min(1000, days_late * 25)
    return LateFee(days_late=days_late, amount_cents=amount_cents)
