from datetime import date

import pytest
from django.core.management import call_command
from django.db import connection

from src.loans.models import Loan


@pytest.mark.django_db
def test_loan_list_matches_characterized_export(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_loan_list_orders_records_by_identifier(client):
    Loan.objects.create(id='L10', member='dee', isbn='123', lent_on=date(2026, 1, 1))

    response = client.get('/loans')
    body = response.content.decode()

    assert response.status_code == 200
    assert body.index('L10;') < body.index('L2;')


@pytest.mark.django_db
def test_loan_lookup_returns_record_or_characterized_not_found(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'

    missing_response = client.get('/loans/unknown')

    assert missing_response.status_code == 404
    assert missing_response['Content-Type'] == 'text/plain'
    assert missing_response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_loan_export_quotes_delimiters_quotes_and_line_breaks(client):
    Loan.objects.create(id='L4', member='a;"b', isbn='123\n456', lent_on=date(2026, 1, 1))

    response = client.get('/loans')

    assert response.status_code == 200
    assert response.content.decode().endswith('L4;"a;""b";"123\n456";2026-01-01;2026-01-15;\n')


@pytest.mark.django_db(transaction=True)
def test_loans_survive_connection_restart_without_reseeding(client):
    Loan.objects.filter(pk='L1').update(member='changed')
    Loan.objects.create(id='L4', member='dee', isbn='123', lent_on=date(2026, 11, 8))

    call_command('migrate', interactive=False, verbosity=0)
    connection.close()

    response = client.get('/loans')

    assert response.status_code == 200
    assert response.content.decode().startswith('L1;changed;9780134685991;2026-01-02;2026-01-16;\n')
    assert response.content.decode().endswith('L4;dee;123;2026-11-08;2026-11-22;\n')


@pytest.mark.django_db
def test_loan_detail_page_has_a_return_path_to_the_catalog(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert 'L1' in response.content.decode()
    assert 'href="/ui/loans/"' in response.content.decode()


@pytest.mark.django_db
def test_catalog_page_shows_seeded_records_and_count(client):
    response = client.get('/ui/loans/')
    body = response.content.decode()

    assert response.status_code == 200
    assert '3 loans in view' in body
    assert 'ISBN 9780134685991' in body
    assert 'href="/ui/loans/L1/"' in body
