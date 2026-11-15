from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class LateFee:
    days_late: int
    amount: Decimal


def calculate_late_fee(due_on: date, returned_on: date | None, today: date) -> LateFee:
    end_date = returned_on or today
    days_late = max(0, (end_date - due_on).days)
    cents = min(days_late * 25, 1000) if days_late > 2 else 0
    return LateFee(days_late=days_late, amount=Decimal(cents) / 100)
