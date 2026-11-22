import json
from pathlib import Path

import pytest

HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/http.json'
    ).read_text(encoding='utf-8')
)
EDGE_CASE_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2]
        / '.migration/characterization/source/goldens/edge-cases.json'
    ).read_text(encoding='utf-8')
)


@pytest.mark.django_db
def test_fee_endpoint_matches_the_characterized_html(client):
    response = client.get('/fees/L3')
    expected = HTTP_GOLDENS['GET /fees/{id}']['response']

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_fee_endpoint_matches_the_unknown_loan_response(client):
    response = client.get('/fees/unknown')
    expected = EDGE_CASE_GOLDENS['GET /fees/unknown']['response']

    assert response.status_code == expected['status']
    assert response['Content-Type'] == expected['content_type']
    assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_payment_endpoint_checks_the_loan_before_gateway_request(client, payment_gateway_server):
    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway_server['requests'] == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('gateway_status', 'gateway_body', 'expected_status'),
    [(200, b'charged\n', 200), (503, b'declined\n', 502)],
)
def test_payment_endpoint_matches_the_gateway_contract(
    client, payment_gateway_server, gateway_status, gateway_body, expected_status
):
    payment_gateway_server['status'] = gateway_status
    payment_gateway_server['body'] = gateway_body

    response = client.post('/payments/L1')

    assert response.status_code == expected_status
    assert response['Content-Type'] == 'text/plain'
    assert response.content == gateway_body
    assert payment_gateway_server['requests'] == [
        ('POST', '/charge?loan=L1', b''),
    ]


@pytest.mark.django_db
def test_fee_page_uses_reading_room_layout_and_posts_to_ui_payment_route(client):
    response = client.get('/ui/fees/L3/')

    assert response.status_code == 200
    assert b'A small nudge, never a surprise' in response.content
    assert b'19 day(s) late' in response.content
    assert b'$4.75' in response.content
    assert b'hx-post="/ui/payments/L3/"' in response.content
    assert b'hx-on::before-swap=' in response.content


@pytest.mark.django_db
def test_ui_payment_error_fragment_renders_gateway_failure(client, payment_gateway_server):
    payment_gateway_server['status'] = 503
    payment_gateway_server['body'] = b'declined\n'

    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'role="alert"' in response.content
    assert b'declined' in response.content
