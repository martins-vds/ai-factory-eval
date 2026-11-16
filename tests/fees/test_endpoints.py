import json
from contextlib import nullcontext
from datetime import date
from email.message import Message
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from src.fees.gateway import HttpPaymentGateway
from src.fees.services import Fee, PaymentGatewayFailure

HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)
GATEWAY_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/gateway.json'
    ).read_text(encoding='utf-8')
)


@pytest.mark.django_db
def test_fee_endpoint_matches_characterized_html(client):
    expected = HTTP_GOLDENS['GET /fees/{id}']['response']

    response = client.get('/fees/L3')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_endpoint_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


def test_fee_endpoint_formats_whole_dollar_amounts(client, monkeypatch):
    class FeeApplication:
        def fee_for(self, loan_id):
            return Fee(date(2026, 1, 10), 8, 200)

    monkeypatch.setattr('src.fees.views.fee_application', FeeApplication())

    response = client.get('/fees/L1')

    assert response.status_code == 200
    assert b'Fee: $2.00' in response.content


@pytest.mark.django_db
def test_payment_endpoint_forwards_the_characterized_gateway_request(client, payment_gateway):
    expected = GATEWAY_GOLDENS['responses']['POST /payments/L1 via test gateway']['response']

    response = client.post('/payments/L1')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_failure_to_bad_gateway(client, payment_gateway):
    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'
    expected = GATEWAY_GOLDENS['responses']['POST /payments/L2 via test gateway']['response']

    response = client.post('/payments/L1')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_does_not_follow_gateway_redirects(client, payment_gateway):
    payment_gateway.status = 302
    payment_gateway.body = b'redirected\n'
    payment_gateway.headers = {'Location': '/other'}

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'redirected\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_endpoint_rejects_unknown_loan_without_calling_gateway(client, payment_gateway):
    expected = GATEWAY_GOLDENS['responses']['POST /payments/unknown via test gateway']['response']

    response = client.post('/payments/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']
    assert payment_gateway.requests == []


@pytest.mark.parametrize(
    ('path', 'method'),
    [
        ('/fees/L1', 'post'),
        ('/payments/L1', 'get'),
        ('/ui/fees/L1/', 'post'),
        ('/ui/payments/L1/', 'get'),
    ],
)
@pytest.mark.django_db
def test_fee_routes_reject_unsupported_methods(client, payment_gateway, path, method):
    response = getattr(client, method)(path)

    assert response.status_code == 405
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_fee_page_returns_not_found_for_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_fee_page_shows_late_fee_and_posts_payment_to_ui_route(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee for L3' in response.content
    assert b'2025-12-15' in response.content
    assert b'19 day(s) late' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content


@pytest.mark.django_db
def test_fee_page_payment_returns_gateway_status_fragment(client, payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert b'id="payment-status"' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_fee_page_payment_shows_gateway_failure_fragment(client, payment_gateway):
    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_fee_page_payment_without_htmx_renders_the_full_page(client, payment_gateway, monkeypatch):
    monkeypatch.setattr(
        'src.fees.views.fee_application.clock.today',
        lambda: date(2026, 1, 24),
    )

    response = client.post('/ui/payments/L1/')

    assert response.status_code == 200
    assert b'Late fee for L1' in response.content
    assert b'2026-01-16' in response.content
    assert b'8 day(s) late' in response.content
    assert b'Fee: $2.00' in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_fee_page_payment_rejects_unknown_loan_without_calling_gateway(client, payment_gateway):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


def test_payment_gateway_uses_the_characterized_default_url(monkeypatch):
    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    requests = []

    class Response:
        status = 200
        headers = Message()

        def read(self):
            return b'charged\n'

    def open_request(request):
        requests.append((request.method, request.full_url))
        return nullcontext(Response())

    monkeypatch.setattr('src.fees.gateway._open', open_request)

    response = HttpPaymentGateway().charge('L1')

    assert response.status == 200
    assert response.body == 'charged\n'
    assert requests == [('POST', 'https://payments.lending-library.invalid/charge?loan=L1')]


def test_interrupted_gateway_call_is_preserved_as_the_gateway_failure_cause(monkeypatch):
    def interrupt(_request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('src.fees.gateway._open', interrupt)

    with pytest.raises(PaymentGatewayFailure) as failure:
        HttpPaymentGateway().charge('L1')

    assert failure.value.body == 'payment gateway unavailable\n'
    assert isinstance(failure.value.__cause__, InterruptedError)


@pytest.mark.django_db
def test_interrupted_payment_request_returns_gateway_failure(monkeypatch, client):
    def interrupt(_request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('src.fees.gateway._open', interrupt)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_io_failure_returns_gateway_failure(monkeypatch, client):
    def unavailable(_request):
        raise OSError('gateway unreachable')

    monkeypatch.setattr('src.fees.gateway._open', unavailable)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_real_browser_can_pay_a_late_fee(live_server, payment_gateway):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/fees/L3/')
            page.get_by_role('button', name='Pay late fee').click()

            status = page.get_by_role('status')
            status.wait_for()
            assert status.inner_text().strip() == 'charged'
            assert payment_gateway.requests == [('POST', '/charge?loan=L3', b'')]
        finally:
            browser.close()
