from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class LateFee:
    days_late: int
    amount: Decimal


def calculate_late_fee(due_on: date, end_on: date) -> LateFee:
    days_late = max(0, (end_on - due_on).days)
    cents = 0 if days_late <= 2 else min(1000, days_late * 25)
    return LateFee(days_late, Decimal(cents) / 100)
