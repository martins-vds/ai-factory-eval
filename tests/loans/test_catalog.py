from datetime import date

import pytest


@pytest.mark.django_db
def test_seeded_catalog_is_listed_in_id_order(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('text/plain')
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_known_loan_is_returned_and_unknown_loan_is_not_found(client):
    known = client.get('/loans/L1')
    unknown = client.get('/loans/unknown')

    assert known.status_code == 200
    assert known.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    assert unknown.status_code == 404
    assert unknown.content.decode() == 'no such loan\n'
    assert known.headers['Content-Type'] == 'text/plain'
    assert unknown.headers['Content-Type'] == 'text/plain'


def test_due_date_is_fourteen_calendar_days_after_lent_date():
    from src.loans.services import due_date

    assert due_date(date(2026, 1, 2)) == date(2026, 1, 16)


@pytest.mark.django_db
def test_export_escapes_delimiter_characters():
    from src.loans.models import Loan
    from src.loans.services import format_loan

    loan = Loan(
        id='L6',
        member='a;b',
        isbn='123;456',
        lent_on=date(2026, 11, 8),
    )

    assert format_loan(loan) == 'L6;"a;b";"123;456";2026-11-08;2026-11-22;'


@pytest.mark.django_db
def test_restart_does_not_overwrite_persisted_loan(client):
    from src.loans.models import Loan

    Loan.objects.filter(id='L1').update(member='persisted')

    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == 'L1;persisted;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_repository_returns_loans_in_id_order():
    from src.loans.repository import LoanRepository

    loans = LoanRepository().list()

    assert [loan.id for loan in loans] == ['L1', 'L2', 'L3']


@pytest.mark.django_db
def test_repository_refuses_absent_lookup():
    from src.loans.repository import LoanRepository

    assert LoanRepository().get('missing') is None


@pytest.mark.django_db
def test_ui_detail_and_absent_detail(client):
    known = client.get('/ui/loans/L1/')
    unknown = client.get('/ui/loans/missing/')

    assert known.status_code == 200
    assert b'Due 2026-01-16' in known.content
    assert unknown.status_code == 404


def test_loan_model_contract():
    from src.loans.models import Loan

    assert Loan._meta.get_field('id').max_length == 32
    assert Loan._meta.get_field('member').max_length == 255
    assert Loan._meta.get_field('isbn').max_length == 255
    assert Loan._meta.get_field('returned_on').null is True
    assert Loan._meta.get_field('returned_on').blank is True
    assert Loan._meta.ordering == ('id',)


def test_loan_due_on_property_uses_fourteen_days():
    from src.loans.models import Loan

    loan = Loan(lent_on=date(2026, 1, 2))

    assert loan.due_on == date(2026, 1, 16)


@pytest.mark.django_db
def test_repository_save_is_available():
    from src.loans.models import Loan
    from src.loans.repository import LoanRepository

    loan = Loan(
        id='L9',
        member='saved',
        isbn='123',
        lent_on=date(2026, 11, 8),
    )

    saved = LoanRepository().save(loan)

    assert saved.pk == 'L9'
    assert LoanRepository().get('L9').member == 'saved'


def test_app_and_route_names_are_composed():
    from django.urls import reverse

    from src.loans.apps import LoansConfig

    assert LoansConfig.default_auto_field == 'django.db.models.BigAutoField'
    assert reverse('loan-list') == '/loans'
    assert reverse('loan-detail', args=['L1']) == '/loans/L1'
    assert reverse('ui-loan-list') == '/ui/loans/'
    assert reverse('ui-loan-detail', args=['L1']) == '/ui/loans/L1/'
