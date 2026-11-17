from datetime import date

import pytest
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_lend_endpoint_creates_a_loan_with_a_fourteen_day_due_date(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4;dee;123;2026-03-01;2026-03-15;\n'
    loan = Loan.objects.get(pk='L4')
    assert loan.lent_on == date(2026, 3, 1)
    assert loan.due_on == date(2026, 3, 15)


@pytest.mark.django_db
def test_lend_endpoint_preserves_whitespace_around_nonblank_fields(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    response = client.post('/loans', {'member': ' dee ', 'isbn': ' 123 '})

    assert response.status_code == 201
    assert response.content.decode() == 'L4; dee ; 123 ;2026-03-01;2026-03-15;\n'
    loan = Loan.objects.get(pk='L4')
    assert loan.member == ' dee '
    assert loan.isbn == ' 123 '


@pytest.mark.parametrize(
    'fields',
    [
        {'member': 'reader'},
        {'isbn': '123'},
        {'member': '', 'isbn': '123'},
        {'member': ' \t ', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': 'reader', 'isbn': '\n '},
    ],
)
@pytest.mark.django_db
def test_lend_endpoint_rejects_missing_or_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_return_endpoint_persists_today_and_rejects_a_second_return(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    first_response = client.post('/loans/L1/return')

    assert first_response.status_code == 200
    assert first_response['Content-Type'] == 'text/plain'
    assert first_response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-03-01\n'
    )
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 3, 1)

    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 2))
    repeated_response = client.post('/loans/L1/return')

    assert repeated_response.status_code == 409
    assert repeated_response['Content-Type'] == 'text/plain'
    assert repeated_response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 3, 1)


@pytest.mark.django_db
def test_return_endpoint_preserves_not_found_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('fields', 'expected_error', 'other_error'),
    [
        ({'isbn': '123'}, b'Member is required.', b'ISBN is required.'),
        ({'member': 'reader'}, b'ISBN is required.', b'Member is required.'),
        ({'member': '  ', 'isbn': '123'}, b'Member is required.', b'ISBN is required.'),
        ({'member': 'reader', 'isbn': '\t'}, b'ISBN is required.', b'Member is required.'),
    ],
)
def test_lending_page_renders_field_errors(client, fields, expected_error, other_error):
    response = client.post('/ui/loans/new/', fields)

    assert response.status_code == 200
    assert expected_error in response.content
    assert other_error not in response.content
    assert Loan.objects.count() == 3


@pytest.mark.parametrize('field', ['member', 'isbn'])
@pytest.mark.django_db
def test_lending_page_rejects_values_longer_than_255_characters(client, field):
    fields = {'member': 'reader', 'isbn': '123'}
    fields[field] = 'x' * 256

    response = client.post('/ui/loans/new/', fields)

    assert response.status_code == 200
    assert b'at most 255 characters' in response.content
    assert Loan.objects.count() == 3


@pytest.mark.parametrize('path', ['/loans/L1/return', '/ui/loans/L1/return/'])
@pytest.mark.django_db
def test_return_routes_reject_get_requests(client, path):
    response = client.get(path)

    assert response.status_code == 405
    assert Loan.objects.get(pk='L1').returned_on is None


@pytest.mark.django_db
def test_ui_return_rejects_unknown_and_already_returned_loans(client):
    original_return_date = Loan.objects.get(pk='L2').returned_on

    unknown_response = client.post(
        '/ui/loans/unknown/return/',
        HTTP_HX_REQUEST='true',
    )
    repeated_response = client.post(
        '/ui/loans/L2/return/',
        HTTP_HX_REQUEST='true',
    )

    assert unknown_response.status_code == 404
    assert unknown_response.content.decode() == 'no such loan\n'
    assert repeated_response.status_code == 409
    assert repeated_response['Content-Type'] == 'text/plain'
    assert repeated_response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_return_date


@pytest.mark.django_db
def test_ui_return_without_htmx_redirects_to_the_loan_detail(client):
    loan = Loan.objects.get(pk='L1')
    loan.returned_on = None
    loan.save(update_fields=['returned_on'])

    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L1/'
    assert Loan.objects.get(pk='L1').returned_on == timezone.localdate()


@pytest.mark.django_db
def test_browser_can_lend_and_return_using_ui_routes(client, monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))

    collection_page = client.get('/ui/loans/')
    lend_page = client.get('/ui/loans/new/')

    assert collection_page.status_code == 200
    assert b'ana \xc2\xb7 ISBN 9780134685991' in collection_page.content
    assert lend_page.status_code == 200
    assert b'Borrower' in lend_page.content
    assert b'ISBN' in lend_page.content
    assert lend_page.content.count(b'class="input input-bordered w-full"') == 2

    lend_response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
    )

    assert lend_response.status_code == 302
    assert lend_response['Location'] == '/ui/loans/L4/'

    return_response = client.post(
        '/ui/loans/L4/return/',
        HTTP_HX_REQUEST='true',
    )

    assert return_response.status_code == 200
    assert b'Returned Mar 1, 2026' in return_response.content
    returned_loan_card = (
        return_response.content.decode().split('Loan L4', 1)[1].split('</article>', 1)[0]
    )
    assert 'Mark returned' not in returned_loan_card
    assert Loan.objects.get(pk='L4').returned_on == date(2026, 3, 1)
