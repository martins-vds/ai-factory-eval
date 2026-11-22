from datetime import date

import pytest
from django.core.management import call_command
from django.db import connection

from src.loans.domain import Loan
from src.loans.repository import DjangoLoanRepository
from src.loans.services import LoanCatalog


class InMemoryLoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def list_all(self):
        return self.loans

    def find_by_id(self, loan_id):
        return next((loan for loan in self.loans if loan.id == loan_id), None)


def test_due_date_is_fourteen_calendar_days_after_lending():
    catalog = LoanCatalog(InMemoryLoanRepository([]))
    loan = Loan(
        id='L4',
        member='dee',
        isbn='123',
        lent_on=date(2026, 11, 8),
        returned_on=None,
    )

    assert loan.due_on == date(2026, 11, 22)
    assert catalog.due_date(loan.lent_on) == date(2026, 11, 22)


def test_catalog_orders_loan_records_by_id():
    loans = [
        Loan('L2', 'bo', '2', date(2026, 1, 10), None),
        Loan('L1', 'ana', '1', date(2026, 1, 2), None),
    ]
    catalog = LoanCatalog(InMemoryLoanRepository(loans))

    assert [loan.id for loan in catalog.list_loans()] == ['L1', 'L2']


def test_unknown_loan_is_not_found_at_use_case_boundary(db):
    catalog = LoanCatalog(DjangoLoanRepository())

    assert catalog.get_loan('missing') is None


@pytest.mark.django_db(transaction=True)
def test_repository_commits_catalog_records_to_postgresql():
    loan = Loan('L4', 'dee', '123', date(2026, 11, 8), None)
    repository = DjangoLoanRepository()

    repository.save(loan)
    connection.close()

    assert repository.find_by_id('L4') == loan


def test_text_export_escapes_field_and_record_delimiters():
    catalog = LoanCatalog(InMemoryLoanRepository([]))
    loan = Loan(
        id='L4',
        member='member;with\nnewline',
        isbn='123;"456',
        lent_on=date(2026, 11, 8),
        returned_on=None,
    )

    assert catalog.format_loan(loan) == (
        'L4;"member;with\nnewline";"123;""456";2026-11-08;2026-11-22;\n'
    )


@pytest.mark.django_db
def test_api_lists_seeded_loans_in_order_with_legacy_text(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_api_gets_one_loan_or_returns_the_legacy_not_found_response(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'

    missing = client.get('/loans/missing')

    assert missing.status_code == 404
    assert missing['Content-Type'] == 'text/plain'
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_ui_detail_and_admin_route(client):
    detail = client.get('/ui/loans/L1/')

    assert detail.status_code == 200
    assert b'9780134685991' in detail.content
    assert client.get('/ui/loans/missing/').status_code == 404
    assert client.get('/admin/login/').status_code == 404


@pytest.mark.django_db
def test_ui_list_renders_the_catalog(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'Loan L1' in response.content


@pytest.mark.django_db(transaction=True)
def test_repository_queries_run_in_atomic_transactions():
    repository = DjangoLoanRepository()
    atomic_states = []

    def record_transaction_state(execute, sql, params, many, context):
        atomic_states.append(connection.in_atomic_block)
        return execute(sql, params, many, context)

    operations = (
        repository.list_all,
        lambda: repository.find_by_id('L1'),
        lambda: repository.save(Loan('L4', 'dee', '123', date(2026, 11, 8), None)),
    )
    for operation in operations:
        atomic_states.clear()
        with connection.execute_wrapper(record_transaction_state):
            operation()
        assert atomic_states and all(atomic_states)


@pytest.mark.django_db(transaction=True)
def test_migration_does_not_reload_seed_data_over_persistent_loans():
    from src.loans.models import LoanRecord

    assert LoanRecord._meta.get_field('returned_on').null

    loan = LoanRecord.objects.get(pk='L1')
    loan.member = 'updated member'
    loan.save(update_fields=['member'])

    call_command('migrate', verbosity=0, interactive=False)
    connection.close()

    assert LoanRecord.objects.get(pk='L1').member == 'updated member'
    assert LoanRecord.objects.count() == 3
