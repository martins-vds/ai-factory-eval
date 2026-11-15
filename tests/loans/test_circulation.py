from datetime import date, timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_lending_creates_due_dated_loan_and_returns_formatted_record(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    fields = response.content.decode().strip().split(';')
    assert fields[:3] == ['L4', 'dee', '123']
    lent_on = date.fromisoformat(fields[3])
    assert lent_on == timezone.localdate()
    assert date.fromisoformat(fields[4]) == lent_on + timedelta(days=14)
    assert fields[5] == ''
    assert client.get('/loans/L4').content.decode() == response.content.decode()


@pytest.mark.django_db
def test_lending_escapes_delimiters_in_export_fields(client):
    response = client.post(
        '/loans',
        {'member': 'reader; guest', 'isbn': '123;456'},
    )
    lent_on = timezone.localdate()

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4;"reader; guest";"123;456";{lent_on.isoformat()};'
        f'{(lent_on + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.parametrize(
    'form_data',
    [
        {'isbn': '123'},
        {'member': 'reader'},
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': '   ', 'isbn': '123'},
        {'member': 'reader', 'isbn': '   '},
    ],
)
@pytest.mark.django_db
def test_lending_rejects_missing_or_blank_required_fields(client, form_data):
    response = client.post('/loans', form_data)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert client.get('/loans').content.decode().count('\n') == 3


@pytest.mark.parametrize(
    'form_data',
    [
        {'member': 'M' * 256, 'isbn': '123'},
        {'member': 'reader', 'isbn': '9' * 256},
    ],
)
@pytest.mark.django_db
def test_lending_enforces_source_field_lengths(client, form_data):
    response = client.post('/loans', form_data)

    assert response.status_code == 400
    assert client.get('/loans').content.decode().count('\n') == 3


@pytest.mark.django_db
def test_lending_preserves_whitespace_around_nonblank_values(client):
    response = client.post('/loans', {'member': ' reader ', 'isbn': ' 123 '})

    assert response.status_code == 201
    fields = response.content.decode().strip().split(';')
    assert fields[1:3] == [' reader ', ' 123 ']


@pytest.mark.django_db
def test_api_endpoints_reject_unsupported_methods(client):
    assert client.put('/loans').status_code == 405
    assert client.put('/loans/L1/return').status_code == 405
    assert client.put('/ui/loans/new/').status_code == 405


@pytest.mark.django_db
def test_reading_room_catalog_renders_existing_loans(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'ana \xc2\xb7 ISBN 9780134685991' in response.content
    assert b'Jan 16, 2026' in response.content


@pytest.mark.django_db
def test_reading_room_has_a_loan_form(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'Lend a book' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content


@pytest.mark.django_db
def test_reading_room_form_reports_field_errors_without_htmx(client):
    response = client.post('/ui/loans/new/', {'member': '', 'isbn': '123'})

    assert response.status_code == 400
    assert b'Lend a book' in response.content
    assert response.content.decode().count('This field is required.') == 1


@pytest.mark.django_db
def test_htmx_lending_creates_a_loan_and_returns_form_feedback(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 201
    assert b'<p role="status" class="alert alert-success">Loan L4 created.</p>' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content
    assert client.get('/loans/L4').content.decode().startswith('L4;reader;123;')


@pytest.mark.django_db
def test_htmx_lending_shows_field_errors_for_blank_values(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '   ', 'isbn': '   '},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 400
    assert b'<form id="loan-form"' in response.content
    assert b'<!doctype html>' not in response.content
    assert response.content.count(b'>This field is required.</p>') == 2
    assert client.get('/loans').content.decode().count('\n') == 3


@pytest.mark.django_db
def test_normal_lending_and_return_forms_redirect_to_the_reading_room(client):
    lending = client.post('/ui/loans/new/', {'member': 'reader', 'isbn': '123'})

    assert lending.status_code == 302
    assert lending['Location'] == '/ui/loans/L4/'
    assert b'Loan L4' in client.get(lending['Location']).content

    returning = client.post('/ui/loans/L4/return/')

    assert returning.status_code == 302
    assert returning['Location'] == '/ui/loans/L4/'
    detail = client.get(returning['Location'])
    assert b'Mark returned' not in detail.content
    assert b'Returned' in detail.content


@pytest.mark.django_db
def test_reading_room_detail_offers_a_return_action(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'Mark returned' in response.content
    assert b'hx-post="/ui/loans/L1/return/"' in response.content


@pytest.mark.django_db
def test_reading_room_rejects_return_for_an_unknown_loan(client):
    response = client.post('/ui/loans/unknown/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_htmx_repeated_return_shows_no_change_feedback(client):
    response = client.post('/ui/loans/L2/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'>This loan has already been returned.</p>' in response.content
    assert b'Jan 20, 2026' in response.content
    assert b'Mark returned' not in response.content


@pytest.mark.django_db
def test_normal_repeated_return_is_rejected_with_the_loan_detail(client):
    response = client.post('/ui/loans/L2/return/')

    assert response.status_code == 409
    assert b'Loan record' in response.content
    assert b'Jan 20, 2026' in response.content
    assert b'Mark returned' not in response.content


@pytest.mark.django_db
def test_htmx_return_records_the_date_and_removes_the_action(client):
    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'Returned' in response.content
    assert b'Mark returned' not in response.content
    assert (
        client.get('/loans/L1').content.decode().endswith(f'{timezone.localdate().isoformat()}\n')
    )


@pytest.mark.django_db
def test_returning_a_loan_sets_and_persists_return_date(client):
    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    fields = response.content.decode().strip().split(';')
    assert fields[:5] == ['L1', 'ana', '9780134685991', '2026-01-02', '2026-01-16']
    assert fields[5] == timezone.localdate().isoformat()
    assert client.get('/loans/L1').content.decode() == response.content.decode()


@pytest.mark.django_db
def test_returning_an_unknown_loan_returns_the_characterized_not_found_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_repeated_return_is_rejected_without_replacing_the_return_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert client.get('/loans/L2').content.decode() == (
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    )


@pytest.mark.django_db
def test_api_return_requires_post(client):
    assert client.get('/loans/L1/return').status_code == 405
    assert client.get('/ui/loans/L1/return/').status_code == 405
