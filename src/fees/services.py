from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.utils import timezone


@dataclass
class LateFee:
    days_late: int
    amount_cents: int

    @property
    def amount(self):
        return Decimal(self.amount_cents) / 100


def calculate_late_fee(loan, *, today: date | None = None) -> LateFee:
    end_date = loan.returned_on or today or timezone.localdate()
    days_late = max(0, (end_date - loan.due_on).days)
    amount_cents = 0 if days_late <= 2 else min(days_late * 25, 1000)
    return LateFee(days_late, amount_cents)
