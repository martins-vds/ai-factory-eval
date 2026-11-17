import json
from datetime import date
from pathlib import Path

import pytest
from django.core.management import call_command
from django.db import IntegrityError, connection

from src.loans.models import Loan
from src.loans.repository import LoanRepository

GOLDENS = Path(__file__).resolve().parents[2] / '.migration' / 'characterization' / 'source' / 'goldens'


@pytest.mark.django_db
def test_seeded_loans_are_listed_in_id_order(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_list_and_lookup_match_the_source_http_goldens(client):
    golden = json.loads((GOLDENS / 'http.json').read_text())

    for key, path in (('GET /loans', '/loans'), ('GET /loans/{id}', '/loans/L1')):
        expected = golden[key]['response']
        response = client.get(path)

        assert response.status_code == expected['status']
        assert response['Content-Type'] == expected['content_type']
        assert response.content.decode() == expected['body']


@pytest.mark.django_db
def test_list_keeps_ids_ordered_when_records_are_inserted_out_of_order(client):
    for loan_id in ('L9', 'L0'):
        LoanRepository.create(
            Loan(
                id=loan_id,
                member='member',
                isbn='123',
                lent_on=date(2026, 1, 1),
            )
        )

    response = client.get('/loans')

    assert [line.split(';', 1)[0] for line in response.content.decode().splitlines()] == [
        'L0',
        'L1',
        'L2',
        'L3',
        'L9',
    ]


@pytest.mark.django_db
def test_existing_loan_lookup_returns_one_formatted_line(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_missing_loan_lookup_returns_the_characterized_not_found_response(client):
    response = client.get('/loans/unknown')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'


def test_django_admin_route_is_not_installed(client):
    assert client.get('/admin/login/').status_code == 404


@pytest.mark.django_db
def test_export_quotes_delimiters_and_line_breaks_in_values(client):
    LoanRepository.save(
        Loan(
            id='L9',
            member='a;"b',
            isbn='123\n456',
            lent_on=date(2026, 1, 1),
        )
    )

    response = client.get('/loans/L9')

    assert response.content.decode() == 'L9;"a;""b";"123\n456";2026-01-01;2026-01-15;\n'


@pytest.mark.django_db
def test_approved_quirk_43_escapes_the_characterized_delimiter_case(client):
    """Ruling #43 replaces ambiguous raw semicolon fields with CSV-quoted target values."""
    source_observation = json.loads((GOLDENS / 'edge-cases.json').read_text())[
        'POST /loans/delimiter-fields'
    ]['response']['body']
    assert source_observation == 'L6;a;b;123;456;2026-11-08;2026-11-22;\n'

    LoanRepository.create(
        Loan(
            id='L6',
            member='a;b',
            isbn='123;456',
            lent_on=date(2026, 11, 8),
        )
    )
    response = client.get('/loans/L6')

    assert response.content.decode() == 'L6;"a;b";"123;456";2026-11-08;2026-11-22;\n'


@pytest.mark.django_db(transaction=True)
def test_saved_loan_survives_database_connection_reopen():
    LoanRepository.save(
        Loan(
            id='L9',
            member='dee',
            isbn='123',
            lent_on=date(2026, 1, 1),
        )
    )
    connection.close()

    assert LoanRepository.find('L9').member == 'dee'


@pytest.mark.django_db(transaction=True)
def test_migration_does_not_replace_existing_seeded_loan_values():
    loan = LoanRepository.find('L1')
    loan.member = 'updated member'
    LoanRepository.save(loan)

    call_command('migrate', interactive=False, verbosity=0)

    assert LoanRepository.find('L1').member == 'updated member'


def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan(id='L9', member='dee', isbn='123', lent_on=date(2024, 2, 20))

    assert loan.due_on == date(2024, 3, 5)


@pytest.mark.django_db
def test_repository_create_does_not_overwrite_an_existing_loan():
    duplicate = Loan(
        id='L1',
        member='replacement',
        isbn='456',
        lent_on=date(2026, 2, 1),
    )

    with pytest.raises(IntegrityError):
        LoanRepository.create(duplicate)

    assert LoanRepository.find('L1').member == 'ana'
