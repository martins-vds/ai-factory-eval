from datetime import timedelta

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.loans.models import Loan


@pytest.mark.django_db
def test_fee_api_returns_characterized_html(client):
    today = timezone.localdate()
    loan = Loan.objects.create(
        id='LL03-DAY-6',
        member='reader',
        isbn='123',
        lent_on=today - timedelta(days=20),
    )

    response = client.get(f'/fees/{loan.id}')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        f'<h1>Late fee for {loan.id}</h1>'
        f'<p>Due {loan.due_on}, 6 day(s) late.</p>'
        '<p class="fee">Fee: $1.50</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_characterized_unknown_loan_response(client):
    response = client.get('/fees/missing')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_reading_room_fee_page_returns_not_found_for_unknown_loan(client):
    response = client.get('/ui/fees/missing/')

    assert response.status_code == 404
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_payment_api_sends_the_gateway_request_and_forwards_success(client, gateway_server):
    loan = Loan.objects.get(pk='L1')

    response = client.post(f'/payments/{loan.id}')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert gateway_server.received == [
        {'method': 'POST', 'path': f'/charge?loan={loan.id}', 'body': ''}
    ]


@pytest.mark.django_db
def test_payment_api_maps_gateway_failure_to_502_and_preserves_body(client, gateway_server):
    gateway_server.responses.append((503, 'declined\n'))

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert gateway_server.received == [{'method': 'POST', 'path': '/charge?loan=L1', 'body': ''}]


@pytest.mark.django_db
def test_payment_api_maps_gateway_redirect_to_502(client, gateway_server):
    gateway_server.responses.append((302, 'redirected\n'))

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'redirected\n'
    assert gateway_server.received == [{'method': 'POST', 'path': '/charge?loan=L1', 'body': ''}]


@pytest.mark.django_db
def test_unknown_payment_does_not_call_gateway(client, gateway_server):
    response = client.post('/payments/missing')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert gateway_server.received == []


@pytest.mark.django_db
def test_reading_room_fee_page_has_htmx_payment_action(client, gateway_server):
    response = client.get('/ui/fees/L1/')

    assert response.status_code == 200
    assert b'>Late fees</h1>' in response.content
    assert b'hx-post="/ui/payments/L1/"' in response.content
    assert b'href="/ui/fees/L2/"' in response.content


@pytest.mark.django_db
def test_htmx_payment_action_shows_gateway_success(client, gateway_server):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert gateway_server.received == [{'method': 'POST', 'path': '/charge?loan=L1', 'body': ''}]


@pytest.mark.django_db
def test_htmx_payment_action_shows_gateway_failure(client, gateway_server):
    gateway_server.responses.append((503, 'declined\n'))

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'<!doctype html>' not in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_regular_payment_action_renders_the_fee_page_with_result(client, gateway_server):
    response = client.post('/ui/payments/L1/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'Payment complete: charged' in response.content
    assert b'hx-post="/ui/payments/L1/"' in response.content
    assert b'href="/ui/fees/L2/"' in response.content


@pytest.mark.django_db
def test_regular_payment_action_renders_not_found_for_unknown_loan(client, gateway_server):
    response = client.post('/ui/payments/missing/')

    assert response.status_code == 404
    assert b'No such loan.' in response.content
    assert gateway_server.received == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/fees/L1', 'post'),
        ('/payments/L1', 'get'),
        ('/ui/fees/L1/', 'post'),
        ('/ui/payments/L1/', 'get'),
    ],
)
def test_fee_and_payment_routes_reject_unsupported_methods(client, gateway_server, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405
    assert gateway_server.received == []


@pytest.mark.django_db
def test_browser_can_pay_late_fee(live_server, gateway_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L1/')
            page.get_by_role('button', name='Pay late fee').click()

            status = page.locator('#payment-status [role="status"]')
            status.wait_for()
            assert 'Payment complete: charged' in status.inner_text()
        finally:
            browser.close()

    assert gateway_server.received == [{'method': 'POST', 'path': '/charge?loan=L1', 'body': ''}]
