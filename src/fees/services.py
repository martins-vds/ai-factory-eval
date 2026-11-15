from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.utils import timezone


@dataclass(frozen=True)
class LateFee:
    days_late: int
    amount: Decimal


def calculate_late_fee(loan, today: date | None = None) -> LateFee:
    assessed_on = loan.returned_on or today or timezone.localdate()
    days_late = max(0, (assessed_on - loan.due_on).days)
    fee_cents = min(max(days_late - 2, 0) * 25, 1000)
    return LateFee(days_late, Decimal(fee_cents) / 100)
