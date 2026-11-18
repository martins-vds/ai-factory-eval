from datetime import date, timedelta

from src.fees.services import FeeQuote, calculate_late_fee


def test_fee_is_twenty_five_cents_per_day_after_grace_period():
    due_on = date(2026, 5, 1)

    fee = calculate_late_fee(due_on, None, due_on + timedelta(days=3))

    assert fee == FeeQuote(late_days=3, amount_cents=75)
