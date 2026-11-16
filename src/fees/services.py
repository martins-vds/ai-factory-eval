from dataclasses import dataclass
from datetime import date


@dataclass
class LateFee:
    days_late: int
    cents: int


def calculate_late_fee(loan, today: date) -> LateFee:
    end_date = loan.returned_on or today
    days_late = max(0, (end_date - loan.due_on).days)
    cents = 0 if days_late <= 2 else min(1000, days_late * 25)
    return LateFee(days_late=days_late, cents=cents)
