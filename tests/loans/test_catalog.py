from datetime import date

import pytest
from django.db import IntegrityError, connection

from src.loans.models import Loan
from src.loans.repositories import LoanRepository


@pytest.mark.django_db
def test_loan_list_matches_characterized_export(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_loan_lookup_returns_characterized_line_or_not_found(client):
    found = client.get('/loans/L1')
    missing = client.get('/loans/unknown')

    assert found.status_code == 200
    assert found['Content-Type'].startswith('text/plain')
    assert found.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    assert missing.status_code == 404
    assert missing['Content-Type'].startswith('text/plain')
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_loan_export_escapes_semicolon_fields_and_includes_due_date(client):
    Loan.objects.create(
        id='L4',
        member='a;\nb',
        isbn='978-0-000-00000-0',
        lent_on=date(2026, 1, 1),
    )

    response = client.get('/loans/L4')

    assert response.content.decode() == ('L4;"a;\nb";978-0-000-00000-0;2026-01-01;2026-01-15;\n')


@pytest.mark.django_db
def test_loan_detail_page_uses_separate_ui_path(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'<h1 id="loan-title"' in response.content
    assert b'Loan L1' in response.content
    assert b'2026-01-16' in response.content


@pytest.mark.django_db
def test_missing_loan_detail_page_is_a_contextual_not_found(client):
    response = client.get('/ui/loans/not-in-catalog/')

    assert response.status_code == 404
    assert b'No such loan' in response.content
    assert b'not-in-catalog' in response.content


@pytest.mark.django_db
def test_catalog_page_lists_seeded_loans(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'href="/ui/loans/L1/"' in response.content
    assert b'9780134685991' in response.content


@pytest.mark.django_db
def test_repository_write_makes_a_loan_retrievable(client):
    LoanRepository.save(
        Loan(
            id='L4',
            member='dee',
            isbn='123',
            lent_on=date(2026, 11, 8),
        )
    )

    response = client.get('/loans/L4')

    assert response.status_code == 200
    assert response.content.decode() == 'L4;dee;123;2026-11-08;2026-11-22;\n'


@pytest.mark.django_db
def test_repository_rolls_back_a_failed_write_without_breaking_reads(client):
    with pytest.raises(IntegrityError):
        LoanRepository.save(
            Loan(
                id='L4',
                member='duplicate',
                isbn=None,
                lent_on=date(2026, 11, 8),
            )
        )

    response = client.get('/loans/L1')

    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_unreturned_loan_is_valid_without_a_return_date():
    loan = Loan(
        id='L4',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 8),
        returned_on=None,
    )

    loan.full_clean()

    assert loan.returned_on is None


@pytest.mark.django_db(transaction=True)
def test_seeded_loan_changes_survive_database_connection_reopen(client):
    Loan.objects.filter(pk='L1').update(member='ana-updated')
    connection.close()

    try:
        response = client.get('/loans/L1')
        assert response.content.decode() == (
            'L1;ana-updated;9780134685991;2026-01-02;2026-01-16;\n'
        )
    finally:
        Loan.objects.filter(pk='L1').update(member='ana')
