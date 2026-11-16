from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LateFee:
    days_late: int
    amount_cents: int


def calculate_late_fee(due_on: date, returned_on: date | None, today: date) -> LateFee:
    days_late = max(0, ((returned_on or today) - due_on).days)
    amount_cents = min(days_late * 25, 1000) if days_late > 2 else 0
    return LateFee(days_late=days_late, amount_cents=amount_cents)
