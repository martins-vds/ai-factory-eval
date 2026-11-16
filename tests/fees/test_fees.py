from datetime import date, timedelta

import pytest
from playwright.sync_api import sync_playwright

from src.fees.payments import HttpPaymentGateway
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
    assert b'Days late' in response.content
    assert b'>19<' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_reading_room_fee_page_returns_characterized_not_found_response(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_pages_display_exact_amount_for_large_fee(client):
    Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2026, 1, 2),
        returned_on=date(2026, 2, 21),
    )

    api_response = client.get('/fees/L9')
    page_response = client.get('/ui/fees/L9/')

    assert api_response.content.decode() == (
        '<h1>Late fee for L9</h1>'
        '<p>Due 2026-01-16, 36 day(s) late.</p>'
        '<p class="fee">Fee: $9.00</p>'
    )
    assert b'<dd class="text-2xl font-bold">$9.00</dd>' in page_response.content
    assert b'<dd>36</dd>' in page_response.content


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
@pytest.mark.parametrize(('gateway_status', 'expected_status'), [(200, 200), (402, 502)])
def test_payment_api_replaces_invalid_gateway_text_bytes(
    client, payment_gateway, gateway_status, expected_status
):
    payment_gateway['status'] = gateway_status
    payment_gateway['body'] = b'charged\xff\n'

    response = client.post('/payments/L1')

    assert response.status_code == expected_status
    assert response.content == 'charged\ufffd\n'.encode()


@pytest.mark.django_db
def test_payment_api_maps_success_status_other_than_200_to_bad_gateway(client, payment_gateway):
    payment_gateway['status'] = 201
    payment_gateway['body'] = b'created\n'

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'created\n'


@pytest.mark.django_db
def test_payment_api_does_not_follow_gateway_redirect(client, payment_gateway):
    payment_gateway['status'] = 302
    payment_gateway['body'] = b'payment moved\n'

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
    assert any(
        record.getMessage() == 'Payment gateway unavailable for loan L1'
        for record in caplog.records
    )
    assert 'InterruptedError: payment request interrupted' in caplog.text


def test_payment_gateway_uses_the_characterized_default_url(monkeypatch):
    requests = []

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return b'charged\n'

    class Opener:
        def open(self, request):
            requests.append((request.method, request.full_url, request.data))
            return Response()

    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr('src.fees.payments.build_opener', lambda *args: Opener())

    response = HttpPaymentGateway().charge('L1')

    assert response.status_code == 200
    assert response.body == 'charged\n'
    assert requests == [
        (
            'POST',
            'https://payments.lending-library.invalid/charge?loan=L1',
            b'',
        )
    ]


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


@pytest.mark.django_db
def test_browser_can_view_and_pay_a_late_fee(live_server, payment_gateway):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            page.get_by_role('heading', name='Late fee for L3').wait_for()
            htmx_available = page.evaluate("typeof window.htmx !== 'undefined'")

            if htmx_available:
                with page.expect_response('**/ui/payments/L3/'):
                    page.get_by_role('button', name='Pay late fee').click()
                page.get_by_role('status').wait_for()
                assert page.get_by_role('status').inner_text() == 'Payment complete: charged'
            else:
                with page.expect_navigation(url='**/ui/fees/L3/'):
                    page.get_by_role('button', name='Pay late fee').click()
                assert page.get_by_role('heading', name='Late fee for L3').is_visible()

            assert payment_gateway['requests'] == [('POST', '/charge?loan=L3', b'')]
        finally:
            browser.close()


@pytest.mark.django_db
def test_reading_room_payment_action_returns_not_found_without_gateway_call(
    client, payment_gateway
):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway['requests'] == []


@pytest.mark.django_db
def test_reading_room_payment_redirects_after_regular_success(client, payment_gateway):
    response = client.post('/ui/payments/L3/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/fees/L3/'
    assert payment_gateway['requests'] == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
def test_reading_room_payment_redirect_escapes_loan_id(client, payment_gateway):
    Loan.objects.create(
        id='L9?x=1',
        member='reader',
        isbn='123',
        lent_on=date(2026, 1, 2),
    )

    response = client.post('/ui/payments/L9%3Fx%3D1/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/fees/L9%3Fx=1/'


@pytest.mark.django_db
def test_reading_room_payment_renders_failure_with_fee_context(client, payment_gateway):
    payment_gateway['status'] = 402
    payment_gateway['body'] = b'declined\n'

    response = client.post('/ui/payments/L3/')

    assert response.status_code == 502
    assert b'role="alert"' in response.content
    assert b'declined' in response.content
    assert b'Late fee for L3' in response.content
    assert b'<dd class="text-2xl font-bold">$4.75</dd>' in response.content
    assert b'<dd>19</dd>' in response.content


@pytest.mark.django_db
def test_interrupted_browser_payment_renders_gateway_failure(client, caplog, monkeypatch):
    class InterruptedOpener:
        def open(self, request):
            raise InterruptedError('payment request interrupted')

    monkeypatch.setattr('src.fees.payments.build_opener', lambda *args: InterruptedOpener())

    response = client.post('/ui/payments/L1/')

    assert response.status_code == 502
    assert b'role="alert"' in response.content
    assert (
        b'<p role="alert" class="alert alert-error">payment gateway unavailable\n</p>'
        in response.content
    )
    assert b'Late fee for L1' in response.content
    assert b'$10.00' in response.content
    assert any(
        record.getMessage() == 'Payment gateway unavailable for loan L1'
        for record in caplog.records
    )
    assert 'InterruptedError: payment request interrupted' in caplog.text


@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('post', '/fees/L1'),
        ('post', '/ui/fees/L1/'),
        ('get', '/ui/payments/L1/'),
    ],
)
def test_fee_and_browser_payment_routes_reject_unsupported_methods(client, method, path):
    response = getattr(client, method)(path)

    assert response.status_code == 405


def test_payment_api_rejects_get_requests(client):
    response = client.get('/payments/L1')

    assert response.status_code == 405
