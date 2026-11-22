from datetime import date

import pytest

from src.loans.models import Loan


@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('post', '/fees/unknown'),
        ('get', '/payments/unknown'),
        ('post', '/ui/fees/unknown/'),
        ('get', '/ui/payments/unknown/'),
    ],
)
def test_fee_and_payment_routes_restrict_http_methods(client, method, path):
    response = getattr(client, method)(path)

    assert response.status_code == 405


@pytest.mark.django_db
def test_io_gateway_failure_becomes_characterized_502(client, monkeypatch):
    Loan.objects.create(
        id='L-pay',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 1),
    )

    def fail_request(_request):
        raise OSError('connection refused')

    monkeypatch.setattr('src.fees.gateway.urlopen', fail_request)

    response = client.post('/payments/L-pay')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'payment gateway unavailable\n'


@pytest.mark.django_db
def test_fee_api_matches_characterized_html_fragment(client):
    Loan.objects.create(
        id='L-test',
        member='dee',
        isbn='123',
        lent_on=date(2025, 12, 1),
        returned_on=date(2026, 1, 3),
    )

    response = client.get('/fees/L-test')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == (
        '<h1>Late fee for L-test</h1><p>Due 2025-12-15, 19 day(s) late.</p>'
        '<p class="fee">Fee: $4.75</p>'
    )


@pytest.mark.django_db
def test_missing_fee_api_response_matches_characterization(client):
    response = client.get('/fees/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/html'
    assert response.content.decode() == '<p>No such loan.</p>'


@pytest.mark.django_db
def test_payment_api_forwards_gateway_request_and_success(client, monkeypatch, payment_gateway):
    Loan.objects.create(
        id='L-pay',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 1),
    )
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/payments/L-pay')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'charged\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L-pay', b'')]


@pytest.mark.django_db
def test_non_200_gateway_response_becomes_502_with_gateway_body(
    client, monkeypatch, payment_gateway
):
    Loan.objects.create(
        id='L-pay',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 1),
    )
    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/payments/L-pay')

    assert response.status_code == 502
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'declined\n'
    assert payment_gateway.requests == [('POST', '/charge?loan=L-pay', b'')]


@pytest.mark.django_db
def test_payment_api_unknown_loan_does_not_call_gateway(client, monkeypatch, payment_gateway):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/payments/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_fee_page_has_payment_action_and_htmx_failure_is_renderable(
    client, monkeypatch, payment_gateway
):
    Loan.objects.create(
        id='L-ui',
        member='dee',
        isbn='123',
        lent_on=date(2025, 12, 1),
        returned_on=date(2026, 1, 3),
    )
    response = client.get('/ui/fees/L-ui/')

    assert response.status_code == 200
    assert b'Fee: $4.75' in response.content
    assert b'hx-post="/ui/payments/L-ui/"' in response.content
    assert b'/ui/payments/L-ui/' in response.content

    payment_gateway.status = 503
    payment_gateway.body = b'\xffdeclined\n'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)
    payment_response = client.post(
        '/ui/payments/L-ui/',
        HTTP_HX_REQUEST='true',
        HTTP_REFERER='/ui/fees/L-ui/',
    )

    assert payment_response.status_code == 502
    assert b'<!doctype html>' not in payment_response.content
    assert b'role="alert"' in payment_response.content
    assert '�declined' in payment_response.content.decode()


@pytest.mark.django_db
def test_fee_page_formats_round_amounts_and_returns_not_found_for_unknown_loan(client):
    Loan.objects.create(
        id='L-round',
        member='dee',
        isbn='123',
        lent_on=date(2025, 12, 2),
        returned_on=date(2026, 1, 5),
    )

    api = client.get('/fees/L-round')
    page = client.get('/ui/fees/L-round/')
    missing = client.get('/ui/fees/unknown/')

    assert api.status_code == 200
    assert b'Fee: $5.00' in api.content
    assert page.status_code == 200
    assert b'Fee: $5.00' in page.content
    assert missing.status_code == 404
    assert b'No such loan.' in missing.content


@pytest.mark.django_db
def test_htmx_payment_success_returns_status_fragment(client, monkeypatch, payment_gateway):
    Loan.objects.create(
        id='L-ui',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 1),
    )
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/ui/payments/L-ui/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'role="status">Payment complete.' in response.content


@pytest.mark.django_db
def test_htmx_payment_for_unknown_loan_returns_error_fragment(client, payment_gateway):
    response = client.post('/ui/payments/unknown/', HTTP_HX_REQUEST='true')
    regular_response = client.post('/ui/payments/unknown/')

    assert response.status_code == 404
    assert b'<!doctype html>' not in response.content
    assert b'role="alert">No such loan.' in response.content
    assert regular_response.status_code == 404
    assert b'No such loan.' in regular_response.content
    assert payment_gateway.requests == []


@pytest.mark.django_db
def test_htmx_payment_gateway_unavailable_returns_error_fragment(client, monkeypatch):
    Loan.objects.create(
        id='L-ui',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 1),
    )

    def fail_request(_request):
        raise OSError('connection refused')

    monkeypatch.setattr('src.fees.gateway.urlopen', fail_request)

    response = client.post('/ui/payments/L-ui/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'<!doctype html>' not in response.content
    assert b'role="alert">payment gateway unavailable' in response.content


@pytest.mark.django_db
def test_regular_payment_failure_renders_fee_page_and_gateway_error(
    client, monkeypatch, payment_gateway
):
    Loan.objects.create(
        id='L-ui',
        member='dee',
        isbn='123',
        lent_on=date(2025, 12, 1),
        returned_on=date(2026, 1, 3),
    )
    payment_gateway.status = 503
    payment_gateway.body = b'declined\n'
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/ui/payments/L-ui/')

    assert response.status_code == 502
    assert b'<!doctype html>' in response.content
    assert b'Fee: $4.75' in response.content
    assert b'role="alert">declined' in response.content


@pytest.mark.django_db
def test_regular_payment_success_redirects_to_fee_page(client, monkeypatch, payment_gateway):
    Loan.objects.create(
        id='L-ui',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 1),
    )
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/ui/payments/L-ui/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/fees/L-ui/'


@pytest.mark.django_db
def test_regular_payment_redirect_escapes_loan_id(client, monkeypatch, payment_gateway):
    loan_id = r'L\example.test'
    Loan.objects.create(
        id=loan_id,
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 1),
    )
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', payment_gateway.url)

    response = client.post('/ui/payments/L%5Cexample.test/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/fees/L%5Cexample.test/'
