import pytest


def assert_error_responses_are_configured(response, target):
    assert response.status_code == 200
    assert response.content.count(b'htmx.config.responseHandling = [') == 1
    assert b'{code: "204", swap: false}' in response.content
    assert b'{code: "[23]..", swap: true}' in response.content
    assert b'{code: "[45]..", swap: true, error: true}' in response.content
    assert b'{code: "...", swap: false}' in response.content
    assert f'hx-target="#{target}"'.encode() in response.content


@pytest.mark.django_db
def test_payment_error_fragment_matches_the_payment_target(client, monkeypatch):
    page = client.get('/ui/fees/L1/')

    assert_error_responses_are_configured(page, 'payment-status')

    def unavailable(_request):
        raise OSError('gateway unreachable')

    monkeypatch.setattr('src.fees.gateway._open', unavailable)
    response = client.post('/ui/payments/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 502
    assert b'id="payment-status"' in response.content
    assert b'role="alert"' in response.content
    assert b'payment gateway unavailable' in response.content


@pytest.mark.django_db
def test_return_error_fragment_matches_the_return_target(client):
    page = client.get('/ui/loans/L1/')

    assert_error_responses_are_configured(page, 'return-status')

    first_return = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')
    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert first_return.status_code == 200
    assert response.status_code == 409
    assert b'id="return-status"' in response.content
    assert b'role="alert"' in response.content
    assert b'already returned' in response.content


@pytest.mark.django_db
def test_lending_error_fragment_matches_the_loan_form_target(client):
    page = client.get('/ui/loans/new/')

    assert_error_responses_are_configured(page, 'loan-form')

    response = client.post(
        '/ui/loans/new/',
        {'member': '', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'id="loan-form"' in response.content
    assert response.content.count(b'This field is required.') == 2
