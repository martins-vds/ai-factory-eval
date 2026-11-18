from datetime import date, timedelta

import pytest


@pytest.mark.parametrize(
    'form_data',
    [
        {},
        {'member': 'dee'},
        {'isbn': '123'},
        {'member': ' ', 'isbn': '123'},
        {'member': 'dee', 'isbn': '\t'},
    ],
)
@pytest.mark.django_db
def test_lending_rejects_missing_or_blank_fields(client, form_data):
    response = client.post('/loans', form_data)

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'
    assert len(client.get('/loans').content.decode().splitlines()) == 3


@pytest.mark.django_db
def test_lending_creates_a_persisted_fourteen_day_loan(client):
    today = date.today()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )
    saved_loan = client.get('/loans/L4')
    assert saved_loan.status_code == 200
    assert saved_loan.content == response.content


@pytest.mark.django_db
def test_returning_a_loan_persists_today_and_returns_the_formatted_record(client):
    today = date.today()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today.isoformat()}\n'
    )
    saved_loan = client.get('/loans/L1')
    assert saved_loan.content == response.content


@pytest.mark.django_db
def test_repeat_return_is_rejected_without_replacing_the_original_date(client):
    original = client.get('/loans/L2')

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert client.get('/loans/L2').content == original.content


@pytest.mark.django_db
def test_returning_an_unknown_loan_keeps_the_characterized_not_found_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_new_loan_page_uses_reading_room_layout(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'Lend a book' in response.content
    assert b'action="/ui/loans/new/"' in response.content


@pytest.mark.django_db
def test_browser_lending_redirects_to_the_updated_collection(client):
    response = client.post('/ui/loans/new/', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    collection = client.get(response['Location'])
    assert b'Loan L4' in collection.content
    assert b'reader \xc2\xb7 ISBN 123' in collection.content


@pytest.mark.parametrize(
    ('form_data', 'field', 'message'),
    [
        ({'member': ' ', 'isbn': '123'}, 'member', 'Enter a member name'),
        ({'member': 'reader', 'isbn': '\t'}, 'isbn', 'Enter an ISBN'),
    ],
)
@pytest.mark.django_db
def test_browser_lending_shows_field_errors_for_blank_values(client, form_data, field, message):
    response = client.post('/ui/loans/new/', form_data)

    assert response.status_code == 400
    assert b'aria-invalid="true"' in response.content
    assert message.encode() in response.content
    assert len(client.get('/loans').content.decode().splitlines()) == 3


@pytest.mark.django_db
def test_browser_return_keeps_original_date_on_repeat(client):
    today = date.today()
    first_return = client.post('/ui/loans/L1/return/')

    assert first_return.status_code == 302
    assert first_return['Location'] == '/ui/loans/'
    collection = client.get(first_return['Location'])
    assert f'Returned {today:%b} {today.day}, {today.year}'.encode() in collection.content

    repeat = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert repeat.status_code == 409
    assert b'This loan was already returned; the original date was kept.' in repeat.content
    assert f'Returned {today:%b} {today.day}, {today.year}'.encode() in repeat.content
