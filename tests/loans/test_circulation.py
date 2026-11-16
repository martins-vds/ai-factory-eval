from datetime import timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_api_creates_a_loan_with_a_fourteen_day_term(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    today = timezone.localdate()
    due_on = today + timedelta(days=14)
    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == f'L4;dee;123;{today};{due_on};\n'

    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.lent_on == today


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('data', 'invalid_field'),
    [
        ({'isbn': '123'}, 'member'),
        ({'member': 'reader'}, 'isbn'),
        ({'member': '', 'isbn': '123'}, 'member'),
        ({'member': 'reader', 'isbn': '   '}, 'isbn'),
    ],
)
def test_lending_api_rejects_missing_or_blank_fields(client, data, invalid_field):
    response = client.post('/loans', data)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
@pytest.mark.parametrize('invalid_field', ['member', 'isbn'])
def test_lending_api_rejects_values_over_source_field_limit(client, invalid_field):
    data = {'member': 'reader', 'isbn': '123'}
    data[invalid_field] = 'x' * 256

    response = client.post('/loans', data)

    assert response.status_code == 400
    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_lending_api_preserves_nonblank_field_whitespace(client):
    response = client.post('/loans', {'member': ' dee ', 'isbn': ' 123 '})

    assert response.status_code == 201
    assert response.content.decode().startswith('L4; dee ; 123 ;')
    loan = Loan.objects.get(pk='L4')
    assert loan.member == ' dee '
    assert loan.isbn == ' 123 '


@pytest.mark.django_db
def test_lending_page_shows_required_errors_for_both_fields(client):
    response = client.post('/ui/loans/new/', {})

    assert response.status_code == 200
    assert b'Enter a member name; blank values are not accepted.' in response.content
    assert b'Enter an ISBN; blank values are not accepted.' in response.content


@pytest.mark.django_db
def test_return_api_records_today_and_returns_the_updated_loan(client):
    response = client.post('/loans/L1/return')

    today = timezone.localdate()
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today}\n')
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_return_api_rejects_a_repeat_and_preserves_the_original_date(client):
    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on.isoformat() == '2026-01-20'


@pytest.mark.django_db
def test_return_api_returns_not_found_for_an_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_api_endpoints_reject_unsupported_methods(client):
    assert client.put('/loans').status_code == 405
    assert client.get('/loans/L1/return').status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('data', 'message'),
    [
        ({'member': '   ', 'isbn': '123'}, b'Enter a member name; blank values are not accepted.'),
        ({'member': 'reader', 'isbn': '   '}, b'Enter an ISBN; blank values are not accepted.'),
    ],
)
def test_lending_page_shows_field_errors_for_blank_values(client, data, message):
    response = client.post('/ui/loans/new/', data)

    assert response.status_code == 200
    assert message in response.content
    assert b'aria-invalid="true"' in response.content
    assert b'hx-post="/ui/loans/new/"' in response.content
    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_lending_page_creates_a_loan_and_returns_to_its_reading_room_detail(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
    )

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'
    detail = client.get(response['Location'])

    assert detail.status_code == 200
    assert b'Loan record \xc2\xb7 L4' in detail.content
    assert b'dee \xc2\xb7 ISBN 123' in detail.content


@pytest.mark.django_db
def test_reading_room_lists_return_controls_only_for_active_loans(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'href="/ui/loans/new/"' in response.content
    assert b'hx-post="/ui/loans/L1/return/"' in response.content
    assert b'hx-post="/ui/loans/L2/return/"' not in response.content


@pytest.mark.django_db
def test_reading_room_return_updates_the_loan_detail(client):
    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L1/'
    detail = client.get(response['Location'])

    assert detail.status_code == 200
    assert b'Returned' in detail.content
    assert Loan.objects.get(pk='L1').returned_on == timezone.localdate()


@pytest.mark.django_db
def test_reading_room_repeat_return_is_rejected_without_overwriting_date(client):
    response = client.post('/ui/loans/L2/return/')

    assert response.status_code == 409
    assert b'This loan has already been returned.' in response.content
    assert b'Loan record \xc2\xb7 L2' in response.content
    assert Loan.objects.get(pk='L2').returned_on.isoformat() == '2026-01-20'


@pytest.mark.django_db
def test_reading_room_return_rejects_unknown_loans_and_unsupported_methods(client):
    missing = client.post('/ui/loans/unknown/return/')

    assert missing.status_code == 404
    assert missing['Content-Type'] == 'text/plain'
    assert missing.content.decode() == 'no such loan\n'
    assert client.get('/ui/loans/L1/return/').status_code == 405
