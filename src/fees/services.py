from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.utils import timezone


@dataclass(frozen=True)
class LateFee:
    due_on: date
    days_late: int
    amount: Decimal


def calculate_late_fee(loan, *, today=None):
    assessed_on = loan.returned_on or today or timezone.localdate()
    days_late = max(0, (assessed_on - loan.due_on).days)
    amount = Decimal('0.00')
    if days_late > 2:
        amount = min(Decimal(days_late) * Decimal('0.25'), Decimal('10.00'))

    return LateFee(loan.due_on, days_late, amount)
