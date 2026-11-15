import csv
import io
from datetime import date

import pytest
from django.core.management import call_command
from django.db import IntegrityError

from src.loans.models import Loan
from src.loans.repository import create_loan, find_loan


@pytest.mark.django_db
def test_loan_list_api_returns_seed_records_as_text(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_loan_detail_api_returns_one_record_with_due_date(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_unknown_loan_detail_returns_not_found_text(client):
    response = client.get('/loans/unknown')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_reapplying_migrations_preserves_persisted_loans():
    Loan.objects.filter(pk='L1').update(member='updated member')
    Loan.objects.create(
        id='L4',
        member='new member',
        isbn='new-isbn',
        lent_on=date(2026, 2, 1),
    )

    call_command('migrate', interactive=False, verbosity=0)

    assert Loan.objects.get(pk='L1').member == 'updated member'
    assert Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_loan_model_matches_its_migrations():
    call_command('makemigrations', 'loans', check=True, dry_run=True, verbosity=0)


@pytest.mark.django_db
def test_repository_commits_new_loan_records():
    loan = create_loan(
        loan_id='L4',
        member='new member',
        isbn='new-isbn',
        lent_on=date(2026, 2, 1),
    )

    assert find_loan('L4').pk == loan.pk


@pytest.mark.django_db
def test_repository_rolls_back_a_failed_write():
    with pytest.raises(IntegrityError):
        create_loan(
            loan_id='L1',
            member='duplicate',
            isbn='duplicate',
            lent_on=date(2026, 2, 1),
        )

    assert Loan.objects.get(pk='L1').member == 'ana'


@pytest.mark.django_db
def test_loan_list_export_escapes_field_and_record_delimiters(client):
    Loan.objects.create(
        id='L4',
        member='a;b\nc',
        isbn='123;456',
        lent_on=date(2026, 2, 1),
    )

    response = client.get('/loans')
    records = list(csv.reader(io.StringIO(response.content.decode()), delimiter=';'))

    assert response.status_code == 200
    assert records[-1] == ['L4', 'a;b\nc', '123;456', '2026-02-01', '2026-02-15', '']
    assert response.content.endswith(b'\n')


@pytest.mark.django_db
def test_catalog_page_renders_seeded_records(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'>ana<' in response.content
    assert b'href="/ui/loans/L1/"' in response.content


@pytest.mark.django_db
def test_loan_page_shows_due_date_and_return_status(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'Loan L1' in response.content
    assert b'Jan 16, 2026' in response.content
    assert b'Not yet returned' in response.content


@pytest.mark.django_db
def test_unreturned_loan_is_valid_with_no_return_date():
    loan = Loan(
        id='L4',
        member='new member',
        isbn='new-isbn',
        lent_on=date(2026, 2, 1),
        returned_on=None,
    )

    loan.full_clean()

    assert loan.returned_on is None


@pytest.mark.django_db
def test_catalog_preserves_long_loan_fields_through_text_api(client):
    loan_id = f'L{"x" * 32}'
    member = 'm' * 256
    isbn = 'i' * 65
    Loan.objects.create(
        id=loan_id,
        member=member,
        isbn=isbn,
        lent_on=date(2026, 2, 1),
    )

    response = client.get(f'/loans/{loan_id}')

    assert response.status_code == 200
    assert response.content.decode() == (f'{loan_id};{member};{isbn};2026-02-01;2026-02-15;\n')
