from datetime import date

import pytest
from django.conf import settings
from django.core.management import call_command
from django.db import IntegrityError
from django.urls import reverse

from src.loans.domain import Loan
from src.loans.models import LoanRecord
from src.loans.repository import DjangoLoanRepository
from src.loans.services import LoanCatalog, LoanNotFound


def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan(
        loan_id='L1',
        member='ana',
        isbn='9780134685991',
        lent_on=date(2026, 1, 2),
        returned_on=None,
    )

    assert loan.due_on == date(2026, 1, 16)
    with pytest.raises(AttributeError):
        loan.member = 'updated'


@pytest.mark.django_db
def test_loan_list_matches_characterized_text(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
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
    assert found['Content-Type'] == 'text/plain'
    assert found.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    assert missing.status_code == 404
    assert missing['Content-Type'] == 'text/plain'
    assert missing.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_catalog_page_renders_seeded_records_and_detail_links(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'The loan catalog' in response.content
    assert b'Record L1' in response.content
    assert b'href="/ui/loans/L1/"' in response.content


@pytest.mark.django_db
def test_loan_page_renders_the_selected_record(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'Loan L1' in response.content
    assert b'Borrowed by ana' not in response.content
    assert b'<dd class="font-medium">ana</dd>' in response.content
    assert b'<dd class="font-medium">9780134685991</dd>' in response.content
    assert b'href="/ui/loans/"' in response.content


@pytest.mark.django_db
def test_missing_loan_page_renders_not_found_message(client):
    response = client.get('/ui/loans/unknown/')

    assert response.status_code == 404
    assert b'Loan not found' in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    'path',
    ['/loans', '/loans/L1', '/ui/loans/', '/ui/loans/L1/'],
)
def test_catalog_routes_reject_non_get_requests(client, path):
    assert client.post(path).status_code == 405


def test_catalog_routes_have_stable_names():
    assert reverse('loan-list') == '/loans'
    assert reverse('loan-detail', kwargs={'loan_id': 'L1'}) == '/loans/L1'
    assert reverse('loan-catalog-page') == '/ui/loans/'
    assert reverse('loan-page', kwargs={'loan_id': 'L1'}) == '/ui/loans/L1/'


def test_returned_date_is_optional_in_the_database_and_forms():
    returned_on = LoanRecord._meta.get_field('returned_on')

    assert returned_on.null is True
    assert returned_on.blank is True


@pytest.mark.django_db
def test_catalog_use_case_refuses_an_unknown_loan():
    catalog = LoanCatalog(DjangoLoanRepository())

    with pytest.raises(LoanNotFound):
        catalog.get_loan('unknown')


@pytest.mark.django_db
def test_catalog_use_case_lists_loans_in_id_order():
    LoanRecord.objects.create(
        id='L0',
        member='dee',
        isbn='123',
        lent_on=date(2026, 1, 1),
    )
    catalog = LoanCatalog(DjangoLoanRepository())

    assert [loan.loan_id for loan in catalog.list_loans()] == ['L0', 'L1', 'L2', 'L3']


@pytest.mark.django_db
def test_catalog_use_case_returns_the_characterized_seed_records():
    catalog = LoanCatalog(DjangoLoanRepository())

    assert [
        (loan.loan_id, loan.member, loan.isbn, loan.lent_on, loan.returned_on)
        for loan in catalog.list_loans()
    ] == [
        ('L1', 'ana', '9780134685991', date(2026, 1, 2), None),
        ('L2', 'bo', '9780596007126', date(2026, 1, 10), date(2026, 1, 20)),
        ('L3', 'cy', '9781617294945', date(2025, 12, 1), date(2026, 1, 3)),
    ]


@pytest.mark.django_db
def test_catalog_use_case_escapes_export_delimiters():
    LoanRecord.objects.create(
        id='L4',
        member='a;"b\nc',
        isbn='123;456',
        lent_on=date(2026, 1, 1),
    )
    catalog = LoanCatalog(DjangoLoanRepository())
    exported = catalog.export_text()

    assert 'L4;"a;""b\nc";"123;456";2026-01-01;2026-01-15;\n' in exported
    assert exported.endswith('\n')


@pytest.mark.django_db
def test_catalog_data_survives_reapplying_migrations():
    seed = LoanRecord.objects.get(id='L1')
    seed.member = 'ana updated'
    seed.save(update_fields=['member'])
    LoanRecord.objects.create(
        id='L4',
        member='dee',
        isbn='123',
        lent_on=date(2026, 1, 1),
    )

    call_command('migrate', verbosity=0)
    catalog = LoanCatalog(DjangoLoanRepository())

    assert catalog.get_loan('L1').member == 'ana updated'
    assert catalog.get_loan('L4').member == 'dee'


@pytest.mark.django_db
def test_repository_rolls_back_a_failed_transaction():
    repository = DjangoLoanRepository()
    duplicate = Loan(
        loan_id='L1',
        member='duplicate',
        isbn='123',
        lent_on=date(2026, 1, 1),
        returned_on=None,
    )

    with pytest.raises(IntegrityError):
        repository.add_loan(duplicate)

    assert repository.get_loan('L1').member == 'ana'


@pytest.mark.django_db
def test_django_admin_is_not_installed_or_routed(client):
    assert 'django.contrib.admin' not in settings.INSTALLED_APPS
    assert client.get('/admin/login/').status_code == 404
