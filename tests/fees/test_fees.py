from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.fees.services import calculate_late_fee


@pytest.mark.parametrize(
    ('days_late', 'expected_amount'),
    [
        (-3, Decimal('0.00')),
        (0, Decimal('0.00')),
        (1, Decimal('0.00')),
        (2, Decimal('0.00')),
        (3, Decimal('0.75')),
        (40, Decimal('10.00')),
        (100, Decimal('10.00')),
    ],
)
def test_late_fee_uses_two_day_grace_and_caps_at_ten_dollars(days_late, expected_amount):
    due_on = date(2026, 1, 1)

    fee = calculate_late_fee(due_on, due_on + timedelta(days=days_late))

    assert fee.days_late == max(0, days_late)
    assert fee.amount == expected_amount
