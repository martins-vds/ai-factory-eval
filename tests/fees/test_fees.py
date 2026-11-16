from datetime import date, timedelta

import pytest

from src.fees.services import calculate_late_fee
from src.loans.models import Loan


@pytest.mark.django_db
def test_fee_page_matches_characterized_html(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1>'
        '<p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.parametrize(
    ('days_late', 'expected_cents'),
    [(0, 0), (2, 0), (3, 75), (60, 1000)],
)
def test_late_fee_observes_grace_period_and_cap(days_late, expected_cents):
    due_on = date(2026, 1, 16)
    loan = Loan(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    fee = calculate_late_fee(loan, due_on + timedelta(days=days_late))

    assert (fee.days_late, fee.cents) == (days_late, expected_cents)


def test_late_fee_uses_return_date_instead_of_today():
    due_on = date(2026, 1, 16)
    loan = Loan(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
        returned_on=date(2026, 1, 19),
    )

    fee = calculate_late_fee(loan, date(2026, 12, 31))

    assert (fee.days_late, fee.cents) == (3, 75)


def test_late_fee_is_zero_when_due_date_has_not_passed():
    due_on = date(2026, 1, 16)
    loan = Loan(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=due_on - timedelta(days=14),
    )

    fee = calculate_late_fee(loan, due_on - timedelta(days=3))

    assert (fee.days_late, fee.cents) == (0, 0)


@pytest.mark.django_db
def test_fee_page_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_reading_room_fee_page_shows_loan_fee_and_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_payment_api_sends_the_characterized_request_and_returns_success(client, payment_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway['requests'] == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_failure_to_bad_gateway(client, payment_gateway):
    payment_gateway['status'] = 402
    payment_gateway['body'] = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert payment_gateway['requests'] == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_follow_gateway_redirect(client, payment_gateway):
    payment_gateway['status'] = 302
    payment_gateway['body'] = b'payment moved\n'
    payment_gateway['location'] = (
        f'http://127.0.0.1:{payment_gateway["port"]}/charge?loan=L1'
    )

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment moved\n'
    assert payment_gateway['requests'] == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_contact_gateway_for_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway['requests'] == []


@pytest.mark.django_db
def test_interrupted_payment_is_a_gateway_failure_and_remains_observable(
    client, caplog, monkeypatch
):
    class InterruptedOpener:
        def open(self, request):
            raise InterruptedError('payment request interrupted')

    monkeypatch.setattr('src.fees.payments.build_opener', lambda *args: InterruptedOpener())

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'
    assert 'InterruptedError: payment request interrupted' in caplog.text


@pytest.mark.django_db
def test_reading_room_payment_action_shows_gateway_success(client, payment_gateway):
    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'Payment complete: charged' in response.content


@pytest.mark.django_db
def test_reading_room_payment_action_shows_gateway_failure(client, payment_gateway):
    payment_gateway['status'] = 503
    payment_gateway['body'] = b'declined\n'

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert b'Payment failed: declined' in response.content


def test_payment_api_rejects_get_requests(client):
    response = client.get('/payments/L1')

    assert response.status_code == 405
