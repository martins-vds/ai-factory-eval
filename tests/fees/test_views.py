import json
from pathlib import Path

import pytest

HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)
EDGE_CASES = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/edge-cases.json'
    ).read_text(encoding='utf-8')
)


@pytest.mark.django_db
def test_fee_api_matches_the_characterized_response(client):
    golden = HTTP_GOLDENS['GET /fees/{id}']

    response = client.get(golden['request']['path'])

    assert response.status_code == golden['response']['status']
    assert response['Content-Type'] == golden['response']['content_type']
    assert response.content.decode() == golden['response']['body']


@pytest.mark.django_db
def test_fee_api_returns_the_characterized_not_found_response(client):
    expected = EDGE_CASES['GET /fees/unknown']['response']

    response = client.get('/fees/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_api_formats_zero_fee_for_an_early_return(client):
    expected = EDGE_CASES['GET /fees/L2 early return']['response']

    response = client.get('/fees/L2')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_payment_api_sends_the_characterized_gateway_request(client, local_payment_gateway):
    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'charged\n'
    assert local_payment_gateway.requests == [
        ('POST', '/charge?loan=L1', b''),
    ]


@pytest.mark.django_db
def test_payment_api_maps_gateway_failure_to_bad_gateway(client, local_payment_gateway):
    local_payment_gateway.response_status = 503
    local_payment_gateway.response_body = b'declined\n'

    response = client.post('/payments/L2')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'declined\n'
    assert local_payment_gateway.requests == [
        ('POST', '/charge?loan=L2', b''),
    ]


@pytest.mark.django_db
def test_payment_api_maps_an_interrupted_gateway_call_to_bad_gateway(client, monkeypatch):
    def interrupt(request):
        raise InterruptedError('request interrupted')

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupt)

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'payment gateway unavailable\n'


@pytest.mark.django_db
def test_payment_api_does_not_call_gateway_for_an_unknown_loan(
    client,
    local_payment_gateway,
):
    expected = EDGE_CASES['POST /payments/unknown']['response']

    response = client.post('/payments/unknown')

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']
    assert local_payment_gateway.requests == []


@pytest.mark.django_db
def test_fee_page_shows_late_fee_and_htmx_payment_action(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'Late fee for L3' in response.content
    assert b'19 day(s) late' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'htmx:beforeSwap' in response.content


@pytest.mark.django_db
def test_unknown_fee_page_renders_a_not_found_message(client):
    response = client.get('/ui/fees/unknown/')

    assert response.status_code == 404
    assert b'<!doctype html>' in response.content
    assert b'role="alert"' in response.content
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_htmx_payment_success_renders_a_status_message(client, local_payment_gateway):
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'id="payment-result"' in response.content
    assert b'role="status"' in response.content
    assert b'Payment received for loan L1.' in response.content
    assert b'charged' in response.content


@pytest.mark.django_db
def test_htmx_payment_failure_renders_an_error_message(
    client,
    local_payment_gateway,
):
    local_payment_gateway.response_status = 503
    local_payment_gateway.response_body = b'declined\n'

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'id="payment-result"' in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_htmx_payment_unknown_loan_renders_the_error_response(client):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'role="alert"' in response.content
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_regular_payment_failure_renders_a_complete_page(
    client,
    local_payment_gateway,
):
    local_payment_gateway.response_status = 503
    local_payment_gateway.response_body = b'declined\n'

    response = client.post('/ui/payments/L1/')

    assert response.status_code == 502
    assert b'<!doctype html>' in response.content
    assert b'role="alert"' in response.content
    assert b'declined' in response.content


@pytest.mark.django_db
def test_regular_payment_success_renders_a_complete_page(
    client,
    local_payment_gateway,
):
    response = client.post('/ui/payments/L1/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'role="status"' in response.content
    assert b'Payment received for loan L1.' in response.content
