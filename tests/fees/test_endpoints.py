import json
from pathlib import Path

import pytest


HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)


@pytest.mark.django_db
def test_fee_api_matches_characterized_html(client):
    golden = HTTP_GOLDENS['GET /fees/{id}']

    response = client.get(golden['request']['path'])

    assert response.status_code == golden['response']['status']
    assert response['Content-Type'] == golden['response']['content_type']
    assert response.content.decode() == golden['response']['body']


@pytest.mark.django_db
def test_fee_api_returns_characterized_not_found_response(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_api_posts_expected_request_and_forwards_success(client, payment_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_payment_api_maps_gateway_failure_to_502_and_preserves_body(client, payment_gateway):
    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response.content.decode() == 'declined\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L2', b'')]


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_unknown_loan(client, payment_gateway):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_payment_action(client):
    response = client.get('/ui/fees/L3/')
    body = response.content.decode()

    assert response.status_code == 200
    assert 'Late fees' in body
    assert '19 day(s) late' in body
    assert 'Fee: $4.75' in body
    assert 'hx-post="/ui/payments/L3/"' in body
    assert 'htmx:beforeSwap' in body


@pytest.mark.django_db
def test_fee_page_renders_not_found_for_unknown_loan(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert 'No such loan.' in response.content.decode()


@pytest.mark.django_db
def test_ui_payment_shows_success_fragment(client, payment_gateway):
    response = client.post(
        '/ui/payments/L1/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert 'Payment complete' in response.content.decode()
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.django_db
def test_ui_payment_renders_gateway_failure_for_htmx(client, payment_gateway):
    response = client.post(
        '/ui/payments/L2/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 502
    assert 'role="alert"' in response.content.decode()
    assert 'declined' in response.content.decode()


@pytest.mark.django_db
def test_payment_api_maps_connection_failure_to_502(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content.decode() == 'payment gateway unavailable\n'
