from datetime import date

import pytest

from src.fees.services import calculate_late_fee


@pytest.mark.parametrize(
    ('today', 'returned_on', 'expected_days', 'expected_cents'),
    [
        (date(2026, 1, 1), None, 0, 0),
        (date(2026, 1, 3), None, 2, 0),
        (date(2026, 1, 4), None, 3, 75),
        (date(2026, 3, 1), None, 59, 1000),
        (date(2026, 2, 1), date(2026, 1, 4), 3, 75),
    ],
)
def test_late_fee_uses_return_date_or_today_with_grace_period_and_cap(
    today,
    returned_on,
    expected_days,
    expected_cents,
):
    fee = calculate_late_fee(
        due_on=date(2026, 1, 1),
        returned_on=returned_on,
        today=today,
    )

    assert fee.days_late == expected_days
    assert fee.amount_cents == expected_cents
