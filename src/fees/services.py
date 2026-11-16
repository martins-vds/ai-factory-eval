from datetime import date
from decimal import Decimal


def calculate_late_fee(due_on: date, through: date) -> tuple[int, Decimal]:
    days_late = max((through - due_on).days, 0)
    fee_cents = min(days_late * 25, 1000) if days_late > 2 else 0
    return days_late, Decimal(fee_cents) / Decimal(100)
