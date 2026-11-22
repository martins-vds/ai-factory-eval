from datetime import date

import pytest

from src.loans.models import LoanRecord


@pytest.mark.django_db
def test_list_returns_characterized_order_and_text(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_get_returns_one_loan_and_missing_loan_is_not_found(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'

    missing = client.get('/loans/unknown')

    assert missing.status_code == 404
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_list_orders_records_by_id(client):
    LoanRecord.objects.create(id='L10', member='ten', isbn='10', lent_on=date(2026, 1, 2))
    LoanRecord.objects.create(id='L4', member='four', isbn='4', lent_on=date(2026, 1, 2))

    response = client.get('/loans')

    assert [line.split(';', 1)[0] for line in response.content.decode().splitlines()] == [
        'L1',
        'L10',
        'L2',
        'L3',
        'L4',
    ]


@pytest.mark.django_db
def test_get_escapes_delimiters_in_record_fields(client):
    LoanRecord.objects.create(
        id='L6',
        member='a;b',
        isbn='123;456',
        lent_on=date(2026, 1, 2),
    )

    response = client.get('/loans/L6')

    assert response.status_code == 200
    assert response.content.decode() == ('L6;"a;b";"123;456";2026-01-02;2026-01-16;\n')


@pytest.mark.django_db
def test_browser_detail_page_renders_loan_fields(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'Loan L1' in response.content
    assert b'9780134685991' in response.content
    assert b'Not yet returned' in response.content


@pytest.mark.django_db
def test_browser_detail_page_renders_not_found_for_unknown_loan(client):
    assert client.get('/ui/loans/unknown/').status_code == 404


def test_admin_route_is_not_available(client):
    assert client.get('/admin/').status_code == 404
