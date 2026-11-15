from dataclasses import dataclass
from datetime import date
from decimal import Decimal

GRACE_PERIOD_DAYS = 2
DAILY_FEE = Decimal('0.25')
MAX_FEE = Decimal('10.00')


@dataclass(frozen=True)
class FeeQuote:
    late_days: int
    amount: Decimal


def calculate_late_fee(due_on: date, returned_on: date | None, today: date) -> FeeQuote:
    effective_date = returned_on or today
    late_days = max(0, (effective_date - due_on).days)
    amount = (
        min(DAILY_FEE * late_days, MAX_FEE) if late_days > GRACE_PERIOD_DAYS else Decimal('0.00')
    )
    return FeeQuote(late_days=late_days, amount=amount)
