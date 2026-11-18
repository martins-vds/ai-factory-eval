from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier

import pytest
from django.db import close_old_connections
from django.test import Client

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_api_creates_a_loan_with_a_fourteen_day_due_date(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post('/loans', {'member': ' dee ', 'isbn': ' 123 '})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4; dee ; 123 ;2026-11-18;2026-12-02;\n'
    loan = Loan.objects.get(pk='L4')
    assert loan.member == ' dee '
    assert loan.isbn == ' 123 '
    assert loan.lent_on == date(2026, 11, 18)
    assert loan.due_on == date(2026, 12, 2)


@pytest.mark.django_db
def test_lending_api_does_not_require_a_browser_csrf_token(monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))
    api_client = Client(enforce_csrf_checks=True)

    response = api_client.post('/loans', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 201
    assert Loan.objects.get(pk='L4').member == 'reader'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fields',
    [
        {'member': '', 'isbn': '123'},
        {'member': '   ', 'isbn': '123'},
        {'member': 'dee', 'isbn': ''},
        {'member': 'dee', 'isbn': '   '},
        {'isbn': '123'},
        {'member': 'dee'},
    ],
)
def test_lending_api_rejects_missing_or_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'
    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_return_api_keeps_the_first_return_date_and_rejects_repeats(client, monkeypatch):
    loan = Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2026, 3, 1),
    )
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    first_return = client.post('/loans/L9/return')

    assert first_return.status_code == 200
    assert first_return.content.decode() == ('L9;reader;123;2026-03-01;2026-03-15;2026-11-18\n')
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 19))

    repeated_return = client.post('/loans/L9/return')

    assert repeated_return.status_code == 409
    assert repeated_return.content.decode() == 'loan already returned\n'
    loan.refresh_from_db()
    assert loan.returned_on == date(2026, 11, 18)


@pytest.mark.django_db
def test_return_api_does_not_require_a_browser_csrf_token(monkeypatch):
    loan = Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2026, 3, 1),
    )
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))
    api_client = Client(enforce_csrf_checks=True)

    response = api_client.post('/loans/L9/return')

    assert response.status_code == 200
    loan.refresh_from_db()
    assert loan.returned_on == date(2026, 11, 18)


@pytest.mark.django_db
def test_return_api_reports_an_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_lending_browser_shows_field_errors_for_blank_values(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '   ', 'isbn': ''},
    )

    assert response.status_code == 200
    assert b'Member name is required.' in response.content
    assert b'ISBN is required.' in response.content
    assert b'aria-invalid="true"' in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_lending_browser_requires_a_csrf_token():
    browser_client = Client(enforce_csrf_checks=True)

    response = browser_client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
    )

    assert response.status_code == 403
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_lending_browser_creates_a_loan_from_the_reading_room(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
    )

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.due_on == date(2026, 12, 2)


@pytest.mark.django_db
def test_reading_room_lend_form_uses_htmx_and_reflects_a_successful_lend(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))
    page = client.get('/ui/loans/')

    assert page.status_code == 200
    assert b'Lend a book' in page.content
    assert b'hx-post="/ui/loans/new/"' in page.content
    assert b'hx-post="/ui/loans/L1/return/"' in page.content

    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Loan created.' in response.content
    assert b'Loan L4' in response.content


@pytest.mark.django_db
def test_returning_a_loan_from_the_browser_updates_its_status(client, monkeypatch):
    loan = Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2026, 3, 1),
    )
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post('/ui/loans/L9/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    loan.refresh_from_db()
    assert loan.returned_on == date(2026, 11, 18)

    detail = client.get('/ui/loans/L9/')

    assert detail.status_code == 200
    assert b'Returned' in detail.content
    assert b'Return L9' not in detail.content


@pytest.mark.django_db
def test_repeated_browser_return_is_visible_and_does_not_change_the_date(client, monkeypatch):
    loan = Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2026, 3, 1),
    )
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))
    client.post('/ui/loans/L9/return/', HTTP_HX_REQUEST='true')
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 19))

    response = client.post('/ui/loans/L9/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'This loan has already been returned.' in response.content
    loan.refresh_from_db()
    assert loan.returned_on == date(2026, 11, 18)


@pytest.mark.django_db
def test_browser_return_route_does_not_change_data_on_get(client, monkeypatch):
    loan = Loan.objects.create(
        id='L9',
        member='reader',
        isbn='123',
        lent_on=date(2026, 3, 1),
    )
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.get('/ui/loans/L9/return/')

    assert response.status_code == 405
    loan.refresh_from_db()
    assert loan.returned_on is None


@pytest.mark.django_db(transaction=True)
def test_concurrent_lending_allocates_distinct_loan_ids(monkeypatch):
    request_count = 8
    start = Barrier(request_count)
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    def lend(index):
        close_old_connections()
        try:
            start.wait(timeout=5)
            response = Client().post(
                '/loans',
                {'member': f'reader-{index}', 'isbn': str(index)},
            )
            return response.status_code, response.content.decode()
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=request_count) as executor:
        results = list(executor.map(lend, range(request_count)))

    assert [status for status, _ in results] == [201] * request_count
    loan_ids = [body.split(';', 1)[0] for _, body in results]
    assert len(set(loan_ids)) == request_count
