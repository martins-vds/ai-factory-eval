import csv
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.db import IntegrityError

from src.loans.models import Loan
from src.loans.repositories import LoanRepository


@pytest.mark.django_db
def test_list_returns_seed_loans_as_characterized_text(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'].split(';', maxsplit=1)[0] == 'text/plain'
    assert response.content == (
        b'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        b'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        b'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_list_orders_loans_by_id_not_insertion_order(client):
    Loan.objects.create(id='L10', member='member', isbn='isbn', lent_on=date(2026, 2, 1))
    Loan.objects.create(id='L4', member='member', isbn='isbn', lent_on=date(2026, 2, 1))

    response = client.get('/loans')
    records = list(csv.reader(StringIO(response.content.decode()), delimiter=';'))

    assert [record[0] for record in records] == ['L1', 'L10', 'L2', 'L3', 'L4']


@pytest.mark.django_db
def test_get_returns_one_loan_as_characterized_text(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'].split(';', maxsplit=1)[0] == 'text/plain'
    assert response.content == b'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_get_returns_characterized_not_found_response(client):
    response = client.get('/loans/unknown')

    assert response.status_code == 404
    assert response['Content-Type'].split(';', maxsplit=1)[0] == 'text/plain'
    assert response.content == b'no such loan\n'


@pytest.mark.django_db(transaction=True)
def test_reapplying_migrations_does_not_replace_persisted_loans(client):
    loan = Loan.objects.get(pk='L1')
    loan.member = 'preserved member'
    loan.save(update_fields=['member'])

    call_command('migrate', interactive=False, verbosity=0)

    response = client.get('/loans')
    assert b'L1;preserved member;9780134685991;2026-01-02;2026-01-16;\n' in response.content


@pytest.mark.django_db
def test_list_escapes_field_and_record_delimiters(client):
    Loan.objects.create(
        id='L4',
        member='a;"b"\nmember2',
        isbn='123;456',
        lent_on=date(2026, 2, 1),
    )

    response = client.get('/loans')
    records = list(csv.reader(StringIO(response.content.decode()), delimiter=';'))

    assert records[-1] == [
        'L4',
        'a;"b"\nmember2',
        '123;456',
        '2026-02-01',
        '2026-02-15',
        '',
    ]


@pytest.mark.django_db
def test_repository_rolls_back_failed_writes_without_poisoning_reads():
    repository = LoanRepository()

    with pytest.raises(IntegrityError):
        repository.create(
            id='L1',
            member='member',
            isbn='isbn',
            lent_on=date(2026, 2, 1),
        )

    assert repository.list().count() == 3


@pytest.mark.django_db
def test_catalog_page_presents_seeded_loans_in_the_reading_room(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'Due Jan 16, 2026' in response.content
    assert b'href="/ui/loans/L1/"' in response.content


@pytest.mark.django_db
def test_admin_login_is_not_exposed(client):
    assert client.get('/admin/login/').status_code == 404


@pytest.mark.django_db
def test_catalog_detail_shows_due_date_and_return_state(client):
    response = client.get('/ui/loans/L2/')

    assert response.status_code == 200
    assert b'9780596007126' in response.content
    assert b'Due Jan 24, 2026' in response.content
    assert b'Returned Jan 20, 2026' in response.content


@pytest.mark.django_db
def test_catalog_detail_returns_not_found_for_unknown_loan(client):
    response = client.get('/ui/loans/unknown/')

    assert response.status_code == 404
