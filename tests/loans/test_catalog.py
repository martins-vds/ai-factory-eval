import csv
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.db import transaction

from src.loans.domain import Loan as LoanEntity
from src.loans.domain import LoanNotFound
from src.loans.models import Loan
from src.loans.repository import DjangoLoanRepository
from src.loans.services import LoanCatalog


class LoanRepositoryStub:
    def __init__(self, loans):
        self.loans = loans

    def list_all(self):
        return self.loans

    def find_by_id(self, loan_id):
        return next((loan for loan in self.loans if loan.id == loan_id), None)


def test_catalog_use_case_orders_loans_and_calculates_due_dates():
    catalog = LoanCatalog(
        LoanRepositoryStub(
            [
                LoanEntity('L2', 'bo', '2', date(2026, 1, 10), None),
                LoanEntity('L1', 'ana', '1', date(2026, 1, 2), None),
            ]
        )
    )

    loans = catalog.list_loans()

    assert [loan.id for loan in loans] == ['L1', 'L2']
    assert loans[0].due_on == date(2026, 1, 16)


@pytest.mark.django_db
def test_catalog_use_case_exposes_the_characterized_seed_records():
    loans = LoanCatalog(DjangoLoanRepository()).list_loans()

    assert [
        (loan.id, loan.member, loan.isbn, loan.lent_on, loan.returned_on) for loan in loans
    ] == [
        ('L1', 'ana', '9780134685991', date(2026, 1, 2), None),
        ('L2', 'bo', '9780596007126', date(2026, 1, 10), date(2026, 1, 20)),
        ('L3', 'cy', '9781617294945', date(2025, 12, 1), date(2026, 1, 3)),
    ]


@pytest.mark.django_db
def test_unreturned_loan_passes_model_validation():
    loan = Loan(id='L4', member='dee', isbn='123', lent_on=date(2026, 2, 1))

    loan.full_clean()
    assert Loan._meta.get_field('returned_on').null is True


def test_catalog_use_case_rejects_an_unknown_loan():
    catalog = LoanCatalog(LoanRepositoryStub([]))

    with pytest.raises(LoanNotFound):
        catalog.get_loan('unknown')


def test_catalog_use_case_escapes_export_delimiters():
    catalog = LoanCatalog(
        LoanRepositoryStub(
            [LoanEntity('L1', 'member;name', 'isbn\nedition', date(2026, 2, 1), None)]
        )
    )

    rows = list(csv.reader(StringIO(catalog.export_loans()), delimiter=';'))

    assert rows == [['L1', 'member;name', 'isbn\nedition', '2026-02-01', '2026-02-15', '']]


@pytest.mark.django_db
def test_list_returns_the_seeded_loans_in_legacy_order(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_lookup_returns_one_loan_or_the_legacy_not_found_response(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'

    missing = client.get('/loans/unknown')
    assert missing.status_code == 404
    assert missing['Content-Type'] == 'text/plain'
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_export_escapes_field_and_record_delimiters(client):
    Loan.objects.create(
        id='L4',
        member='member;name',
        isbn='isbn\nedition',
        lent_on=date(2026, 2, 1),
    )

    response = client.get('/loans')
    rows = list(csv.reader(StringIO(response.content.decode()), delimiter=';'))

    assert rows[-1] == [
        'L4',
        'member;name',
        'isbn\nedition',
        '2026-02-01',
        '2026-02-15',
        '',
    ]


@pytest.mark.django_db
def test_existing_loan_survives_a_repeated_migration(client):
    Loan.objects.filter(pk='L1').update(member='persistent member')

    call_command('migrate', interactive=False, verbosity=0)

    response = client.get('/loans/L1')
    assert response.content.decode() == (
        'L1;persistent member;9780134685991;2026-01-02;2026-01-16;\n'
    )


@pytest.mark.django_db
def test_catalog_use_case_reads_persisted_data_after_a_repeated_migration():
    Loan.objects.filter(pk='L1').update(member='persistent member')
    call_command('migrate', interactive=False, verbosity=0)

    loan = LoanCatalog(DjangoLoanRepository()).get_loan('L1')

    assert loan.member == 'persistent member'


@pytest.mark.django_db
def test_repository_persists_and_reads_a_loan_record():
    repository = DjangoLoanRepository()
    loan = LoanEntity('L4', 'dee', '123', date(2026, 2, 1), None)

    assert repository.save(loan) == loan
    assert repository.find_by_id('L4') == loan


@pytest.mark.django_db
def test_repository_write_rolls_back_with_its_transaction():
    repository = DjangoLoanRepository()
    loan = LoanEntity('L4', 'dee', '123', date(2026, 2, 1), None)

    with pytest.raises(RuntimeError), transaction.atomic():
        repository.save(loan)
        raise RuntimeError('abort transaction')

    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_admin_is_not_exposed(client):
    assert client.get('/admin/').status_code == 404


@pytest.mark.django_db
def test_catalog_page_references_pinned_ui_assets(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    html = response.content.decode()
    assert '/static/css/tailwind.css' in html
    assert 'daisyui@4.12.24' in html
    assert 'htmx.org@2.0.11' in html
    assert '9780134685991' in html


@pytest.mark.django_db
def test_catalog_detail_page_shows_loan_and_missing_page_identifies_unknown_loan(client):
    detail = client.get('/ui/loans/L1/')
    assert detail.status_code == 200
    assert b'9780134685991' in detail.content
    assert b'ana' in detail.content

    missing = client.get('/ui/loans/unknown/')
    assert missing.status_code == 404
    assert b'unknown' in missing.content


@pytest.mark.django_db
def test_missing_catalog_page_renders_a_not_found_response(client):
    response = client.get('/ui/loans/unknown/')

    assert response.status_code == 404
    assert b"We couldn't find that loan." in response.content
