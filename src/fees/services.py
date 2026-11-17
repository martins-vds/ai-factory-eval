from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LateFee:
    days_late: int
    amount_cents: int

    @property
    def formatted_amount(self):
        return f'${self.amount_cents // 100}.{self.amount_cents % 100:02d}'


def calculate_late_fee(due_on: date, returned_on: date | None, today: date) -> LateFee:
    days_late = max(0, ((returned_on or today) - due_on).days)
    amount_cents = 0 if days_late <= 2 else min(1000, days_late * 25)
    return LateFee(days_late, amount_cents)
