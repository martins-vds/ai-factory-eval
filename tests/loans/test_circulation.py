from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from threading import Barrier

import pytest
from django.db import close_old_connections
from django.test import Client


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
    assert response['Content-Type'] == 'text/plain'
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


@pytest.mark.django_db(transaction=True)
def test_concurrent_lending_allocates_distinct_ids():
    requests_started = Barrier(8)

    def lend(index):
        close_old_connections()
        try:
            requests_started.wait()
            return Client().post(
                '/loans',
                {'member': f'reader-{index}', 'isbn': str(index)},
            )
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=8) as workers:
        responses = list(workers.map(lend, range(8)))

    assert all(response.status_code == 201 for response in responses)
    loan_ids = {response.content.decode().split(';', 1)[0] for response in responses}
    assert loan_ids == {f'L{number}' for number in range(4, 12)}


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
def test_browser_lending_shows_both_field_errors_when_fields_are_missing(client):
    response = client.post('/ui/loans/new/', {})

    assert response.status_code == 400
    assert (
        b'<span class="mt-1 text-sm text-[#a94e37]" role="alert">'
        b'Enter a member name; blank values are not accepted.</span>'
    ) in response.content
    assert (
        b'<span class="mt-1 text-sm text-[#a94e37]" role="alert">'
        b'Enter an ISBN; blank values are not accepted.</span>'
    ) in response.content
    assert response.content.count(b'value=""') == 2


@pytest.mark.django_db
def test_htmx_lending_redirects_to_the_collection(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/ui/loans/'
    assert client.get('/loans/L4').status_code == 200


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
    assert (
        b'role="status">This loan was already returned; the original date was kept.</div>'
        in repeat.content
    )
    assert f'Returned {today:%b} {today.day}, {today.year}'.encode() in repeat.content


@pytest.mark.django_db
def test_browser_return_of_an_unknown_loan_renders_not_found_feedback(client):
    response = client.post('/ui/loans/unknown/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'role="status">No such loan.</div>' in response.content


@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('post', '/ui/loans/'),
        ('post', '/ui/loans/L1/'),
        ('put', '/ui/loans/new/'),
        ('get', '/ui/loans/L1/return/'),
        ('put', '/loans'),
        ('post', '/loans/L1'),
        ('get', '/loans/L1/return'),
    ],
)
@pytest.mark.django_db
def test_circulation_routes_reject_unsupported_methods(client, method, path):
    response = getattr(client, method)(path)

    assert response.status_code == 405
