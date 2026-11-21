from datetime import date

import pytest
from django.test import Client

from src.loans.models import Loan
from src.loans.models import seed_records_if_empty
from src.loans.services import CatalogService


@pytest.mark.django_db
def test_seed_records_are_available_in_id_order():
    response = Client().get('/loans')

    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('text/plain')
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_unknown_loan_returns_404_text():
    response = Client().get('/loans/unknown')

    assert response.status_code == 404
    assert response.content == b'no such loan\n'


@pytest.mark.django_db
def test_due_date_is_fourteen_calendar_days_after_lent_on():
    loan = Loan(
        id='LX',
        member='reader',
        isbn='123',
        lent_on=date(2026, 11, 8),
    )

    assert CatalogService().due_on(loan) == date(2026, 11, 22)


@pytest.mark.django_db
def test_export_escapes_delimiter_and_line_break_characters():
    loan = Loan(
        id='L6',
        member='a;b',
        isbn='123\n456',
        lent_on=date(2026, 11, 8),
    )

    assert CatalogService().export_line(loan) == (
        'L6;"a;b";"123\n456";2026-11-08;2026-11-22;\n'
    )


@pytest.mark.django_db
def test_seeding_does_not_replace_persisted_records():
    Loan.objects.create(
        id='L4',
        member='persisted',
        isbn='123',
        lent_on=date(2026, 11, 8),
    )

    seed_records_if_empty()

    assert Loan.objects.filter(id='L4').exists()
    assert Loan.objects.count() == 4
