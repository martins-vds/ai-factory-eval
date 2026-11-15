from datetime import date
from decimal import Decimal

from src.fees.services import calculate_late_fee


def test_late_fee_charges_twenty_five_cents_after_two_grace_days():
    fee = calculate_late_fee(
        due_on=date(2026, 11, 12),
        returned_on=None,
        today=date(2026, 11, 15),
    )

    assert fee.days_late == 3
    assert fee.amount == Decimal('0.25')
