from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LateFee:
    days_late: int
    amount_cents: int


def calculate_late_fee(*, due_on: date, returned_on: date | None, today: date) -> LateFee:
    end_date = returned_on or today
    days_late = max(0, (end_date - due_on).days)
    amount_cents = 0 if days_late <= 2 else min(1000, days_late * 25)
    return LateFee(days_late=days_late, amount_cents=amount_cents)
