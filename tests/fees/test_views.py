from dataclasses import dataclass

import pytest


@dataclass
class GatewayResponse:
    status_code: int
    body: str


class PaymentGateway:
    def __init__(self, status_code=200, body='charged\n', error=None):
        self.status_code = status_code
        self.body = body
        self.error = error
        self.charge_calls = []

    def charge(self, loan_id):
        self.charge_calls.append(loan_id)
        if self.error:
            raise self.error
        return GatewayResponse(self.status_code, self.body)


@pytest.mark.django_db
def test_fee_api_matches_the_characterized_html(client):
    response = client.get('/fees/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content == b'<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_api_returns_gateway_success_unchanged(client, monkeypatch):
    from src.fees import views

    gateway = PaymentGateway()
    monkeypatch.setattr(views.payment_application, 'gateway', gateway)

    response = client.post('/payments/L3')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert gateway.charge_calls == ['L3']


@pytest.mark.django_db
def test_payment_api_maps_gateway_failure_to_bad_gateway(client, monkeypatch):
    from src.fees import views

    gateway = PaymentGateway(status_code=503, body='declined\n')
    monkeypatch.setattr(views.payment_application, 'gateway', gateway)

    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_unknown_loan(client, monkeypatch):
    from src.fees import views

    gateway = PaymentGateway()
    monkeypatch.setattr(views.payment_application, 'gateway', gateway)

    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'
    assert gateway.charge_calls == []


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_offers_htmx_payment(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'<h1' in response.content
    assert b'Late fee for L3' in response.content
    assert b'Due 2025-12-15, 19 day(s) late.' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'action="/ui/payments/L3/"' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'hx-on::before-swap=' in response.content


@pytest.mark.django_db
def test_fee_page_returns_a_not_found_page_for_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_htmx_payment_page_renders_gateway_failure_for_swap(client, monkeypatch):
    from src.fees import views

    gateway = PaymentGateway(status_code=503, body='declined\n')
    monkeypatch.setattr(views.payment_application, 'gateway', gateway)

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_htmx_payment_success_renders_status(client, monkeypatch):
    from src.fees import views

    gateway = PaymentGateway()
    monkeypatch.setattr(views.payment_application, 'gateway', gateway)

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'Payment received.' in response.content


@pytest.mark.django_db
def test_payment_page_response_handles_gateway_interruption(client, monkeypatch):
    from src.fees import views
    from src.fees.services import PaymentGatewayError

    interruption = InterruptedError('request interrupted')
    failure = PaymentGatewayError('payment gateway unavailable')
    failure.__cause__ = interruption
    gateway = PaymentGateway(error=failure)
    monkeypatch.setattr(views.payment_application, 'gateway', gateway)

    response = client.post('/ui/payments/L3/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'payment gateway unavailable' in response.content
    assert failure.__cause__ is interruption
