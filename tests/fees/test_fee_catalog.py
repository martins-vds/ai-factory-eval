from io import BytesIO
from urllib.error import HTTPError

import pytest

from src.fees.gateway import HttpPaymentGateway


@pytest.mark.django_db
def test_fee_endpoint_returns_characterized_l3_fee(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1>'
        '<p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_endpoint_returns_zero_for_early_returned_loan(client):
    response = client.get('/fees/L2')

    assert response.status_code == 200
    assert 'Due 2026-01-24, 0 day(s) late.' in response.content.decode()
    assert 'Fee: $0.00' in response.content.decode()


@pytest.mark.django_db
def test_fee_endpoint_returns_characterized_not_found_fragment(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_endpoint_returns_404_before_gateway(client, monkeypatch):
    calls = []
    monkeypatch.setattr(
        'src.fees.composition.payment_application.gateway_charge',
        lambda loan_id: calls.append(loan_id),
    )

    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'
    assert calls == []


@pytest.mark.django_db
def test_payment_endpoint_forwards_gateway_success(client, monkeypatch):
    monkeypatch.setattr(
        'src.fees.composition.payment_application.gateway_charge',
        lambda loan_id: (200, 'charged'),
    )

    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'charged'


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_failure_to_502(client, monkeypatch):
    monkeypatch.setattr(
        'src.fees.composition.payment_application.gateway_charge',
        lambda loan_id: (503, 'declined'),
    )

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response.content.decode() == 'declined'


@pytest.mark.django_db
def test_payment_endpoint_maps_gateway_io_failure_to_502(client, monkeypatch):
    def unavailable(_loan_id):
        raise OSError('unavailable')

    monkeypatch.setattr(
        'src.fees.composition.payment_application.gateway_charge',
        unavailable,
    )

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response.content.decode() == 'payment gateway unavailable\n'


@pytest.mark.django_db
def test_browser_fee_page_has_reading_room_layout_and_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'Late fee' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'class="card' in response.content


@pytest.mark.django_db
def test_browser_htmx_payment_success_replaces_status(client, monkeypatch):
    monkeypatch.setattr(
        'src.fees.composition.payment_application.gateway_charge',
        lambda loan_id: (200, 'charged'),
    )

    response = client.post(
        '/ui/payments/L3/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'role="status"' in response.content
    assert b'charged' in response.content


@pytest.mark.django_db
def test_browser_htmx_payment_failure_replaces_status_with_error(client, monkeypatch):
    monkeypatch.setattr(
        'src.fees.composition.payment_application.gateway_charge',
        lambda loan_id: (503, 'declined'),
    )

    response = client.post(
        '/ui/payments/L3/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 502
    assert b'<!doctype html>' not in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_payment_write_routes_reject_get(client):
    api_response = client.get('/payments/L1')
    ui_response = client.get('/ui/payments/L1/')

    assert api_response.status_code == 405
    assert ui_response.status_code == 405


@pytest.mark.django_db
def test_browser_regular_payment_success_redirects_to_fee_page(client, monkeypatch):
    monkeypatch.setattr(
        'src.fees.composition.payment_application.gateway_charge',
        lambda loan_id: (200, 'charged'),
    )

    response = client.post('/ui/payments/L3/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/fees/L3/'


@pytest.mark.django_db
def test_browser_regular_payment_failure_returns_gateway_error(client, monkeypatch):
    monkeypatch.setattr(
        'src.fees.composition.payment_application.gateway_charge',
        lambda loan_id: (503, 'declined'),
    )

    response = client.post('/ui/payments/L3/')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'declined'


def test_http_gateway_posts_exact_loan_charge_request(monkeypatch):
    captured = {}

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'charged'

    def fake_urlopen(request, timeout):
        captured['request'] = request
        captured['timeout'] = timeout
        return Response()

    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'https://gateway.example/')
    monkeypatch.setattr('src.fees.gateway.urlopen', fake_urlopen)

    status, body = HttpPaymentGateway().charge('L 1')

    assert status == 200
    assert body == 'charged'
    assert captured['timeout'] == 5
    assert captured['request'].get_method() == 'POST'
    assert captured['request'].full_url == 'https://gateway.example/charge?loan=L+1'


def test_http_gateway_preserves_http_error_response(monkeypatch):
    def unavailable(_request, timeout):
        raise HTTPError(
            'https://gateway.example/charge',
            503,
            'Service Unavailable',
            {},
            BytesIO(b'declined'),
        )

    monkeypatch.setattr('src.fees.gateway.urlopen', unavailable)

    status, body = HttpPaymentGateway().charge('L1')

    assert status == 503
    assert body == 'declined'
