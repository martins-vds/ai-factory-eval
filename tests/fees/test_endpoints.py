import json
from datetime import date
from pathlib import Path

import pytest

from src.loans.models import Loan

HTTP_GOLDENS = json.loads(
    (
        Path(__file__).resolve().parents[2] / '.migration/characterization/source/goldens/http.json'
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
def test_payment_api_does_not_follow_gateway_redirects(client, payment_gateway):
    response = client.post('/payments/L3')

    assert response.status_code == 502
    assert response.content.decode() == 'redirected\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L3', b'')]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('loan_id', 'status'),
    [('L4', 200), ('L5', 502)],
)
def test_payment_api_decodes_gateway_bodies_with_replacement(
    client, payment_gateway, loan_id, status
):
    Loan.objects.create(
        id=loan_id,
        member='reader',
        isbn='123',
        lent_on=date(2026, 1, 1),
    )

    response = client.post(f'/payments/{loan_id}')

    assert response.status_code == status
    assert response.content.decode() == '\ufffd'
    assert payment_gateway.requests == [('POST', f'/charge?loan={loan_id}', b'')]


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
    assert 'L1 · ana' in body
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
def test_ui_payment_renders_unknown_loan_error_for_htmx(client, payment_gateway):
    response = client.post(
        '/ui/payments/unknown/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 404
    assert 'role="alert"' in response.content.decode()
    assert 'no such loan' in response.content.decode()
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_regular_ui_payment_returns_not_found_page_for_unknown_loan(client, payment_gateway):
    response = client.post('/ui/payments/unknown/')

    assert response.status_code == 404
    assert 'No such loan.' in response.content.decode()
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_regular_ui_payment_renders_fee_and_loan_list(client, payment_gateway):
    response = client.post('/ui/payments/L1/')
    body = response.content.decode()

    assert response.status_code == 200
    assert 'Payment complete' in body
    assert 'Fee: $10.00' in body
    assert 'L1 · ana' in body
    assert payment_gateway.requests == [('POST', '/charge?loan=L1', b'')]


@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('post', '/fees/L1'),
        ('get', '/payments/L1'),
        ('post', '/ui/fees/L1/'),
        ('get', '/ui/payments/L1/'),
    ],
)
def test_fee_and_payment_routes_reject_unsupported_methods(client, method, path):
    response = getattr(client, method)(path)

    assert response.status_code == 405


@pytest.mark.django_db
def test_payment_api_maps_connection_failure_to_502(client, monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:1')

    response = client.post('/payments/L1')

    assert response.status_code == 502
    assert response.content.decode() == 'payment gateway unavailable\n'


@pytest.mark.django_db
def test_gateway_url_trims_trailing_slash_without_removing_path(
    client, payment_gateway, monkeypatch
):
    monkeypatch.setenv(
        'PAYMENT_GATEWAY_URL',
        f'http://127.0.0.1:{payment_gateway.server_port}/X/',
    )

    response = client.post('/payments/L1')

    assert response.status_code == 200
    assert payment_gateway.requests == [('POST', '/X/charge?loan=L1', b'')]
