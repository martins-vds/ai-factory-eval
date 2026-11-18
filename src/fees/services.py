from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FeeQuote:
    late_days: int
    amount_cents: int


def calculate_late_fee(due_on: date, returned_on: date | None, today: date) -> FeeQuote:
    late_days = max(0, ((returned_on or today) - due_on).days)
    amount_cents = 0 if late_days <= 2 else min(late_days * 25, 1000)
    return FeeQuote(late_days=late_days, amount_cents=amount_cents)
