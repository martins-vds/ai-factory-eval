from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from django.utils import timezone

from src.fees.services import FeeApplication
from src.loans.models import Loan


@pytest.mark.parametrize(
    ('returned_on', 'today', 'expected_late_days', 'expected_amount_cents'),
    [
        (date(2025, 1, 1), date(2025, 1, 21), 0, 0),
        (None, date(2025, 1, 21), 19, 475),
    ],
)
def test_fee_application_clamps_days_at_zero_and_uses_clock_when_not_returned(
    returned_on, today, expected_late_days, expected_amount_cents
):
    loan = SimpleNamespace(
        id='L1',
        due_on=date(2025, 1, 2),
        returned_on=returned_on,
    )
    repository = Mock()
    repository.find.return_value = loan
    clock = Mock()
    clock.today.return_value = today

    fee = FeeApplication(repository, clock).calculate('L1')

    assert fee.late_days == expected_late_days
    assert fee.amount_cents == expected_amount_cents


@pytest.mark.parametrize(
    ('late_days', 'expected_amount_cents'),
    [(2, 0), (3, 75)],
)
def test_fee_application_waives_two_days_and_charges_twenty_five_cents_per_day(
    late_days, expected_amount_cents
):
    loan = SimpleNamespace(
        id='L1',
        due_on=date(2025, 1, 1),
        returned_on=date(2025, 1, 1) + timedelta(days=late_days),
    )
    repository = Mock()
    repository.find.return_value = loan

    fee = FeeApplication(repository, Mock()).calculate('L1')

    assert fee.amount_cents == expected_amount_cents


@pytest.mark.parametrize('late_days', [40, 41])
def test_fee_application_caps_amount_at_ten_dollars(late_days):
    loan = SimpleNamespace(
        id='L1',
        due_on=date(2025, 1, 1),
        returned_on=date(2025, 1, 1) + timedelta(days=late_days),
    )
    repository = Mock()
    repository.find.return_value = loan

    fee = FeeApplication(repository, Mock()).calculate('L1')

    assert fee.amount_cents == 1000


def test_fee_application_returns_none_for_unknown_loan():
    repository = Mock()
    repository.find.return_value = None

    fee = FeeApplication(repository, Mock()).calculate('unknown')

    assert fee is None


def test_fee_application_returns_fields_required_by_fee_page():
    due_on = date(2025, 1, 1)
    loan = SimpleNamespace(
        id='L1',
        due_on=due_on,
        returned_on=date(2025, 1, 4),
    )
    repository = Mock()
    repository.find.return_value = loan

    fee = FeeApplication(repository, Mock()).calculate('L1')

    assert (fee.loan_id, fee.due_on, fee.late_days, fee.formatted_amount) == (
        'L1',
        due_on,
        3,
        '0.75',
    )


@pytest.mark.django_db
def test_fee_endpoint_displays_characterized_days_and_amount(client):
    today = timezone.localdate()
    due_on = today - timedelta(days=19)
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    response = client.get('/fees/L9')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        f'<h1>Late fee for L9</h1><p>Due {due_on.isoformat()}, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('late_days', 'expected_amount'),
    [(0, '0.00'), (2, '0.00'), (3, '0.75'), (40, '10.00'), (41, '10.00')],
)
def test_fee_endpoint_applies_grace_period_and_cap(client, late_days, expected_amount):
    today = timezone.localdate()
    due_on = today - timedelta(days=late_days)
    loan_id = f'L{late_days + 10}'
    Loan.objects.create(
        id=loan_id,
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    response = client.get(f'/fees/{loan_id}')

    assert response.status_code == 200
    assert f'{late_days} day(s) late'.encode() in response.content
    assert f'Fee: ${expected_amount}' in response.content.decode()


@pytest.mark.django_db
def test_fee_endpoint_uses_return_date_instead_of_current_date(client):
    today = timezone.localdate()
    due_on = today - timedelta(days=19)
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
        returned_on=due_on + timedelta(days=2),
    )

    response = client.get('/fees/L9')

    assert response.status_code == 200
    assert b'2 day(s) late' in response.content
    assert b'Fee: $0.00' in response.content


@pytest.mark.django_db
def test_fee_endpoint_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_returns_not_found_for_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_reading_room_fee_page_shows_fee_and_htmx_payment_action(client):
    today = timezone.localdate()
    due_on = today - timedelta(days=19)
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    response = client.get('/ui/fees/L9/')

    assert response.status_code == 200
    assert b'Late fee for L9</h1>' in response.content
    assert due_on.isoformat().encode() in response.content
    assert b'>19</dd>' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L9/"' in response.content
