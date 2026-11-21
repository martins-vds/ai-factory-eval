from datetime import date

import pytest
from django.core.management import call_command
from django.db import IntegrityError

from src.loans.domain import Loan
from src.loans.models import LoanRecord
from src.loans.repository import DjangoLoanRepository
from src.loans.services import GetLoan, ListLoans, LoanNotFound, SaveLoan


@pytest.mark.django_db
def test_api_lists_seeded_loans_as_legacy_text(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_api_returns_plain_text_not_found_for_unknown_loan(client):
    response = client.get('/loans/unknown')

    assert response.status_code == 404
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'


@pytest.mark.django_db
def test_api_returns_one_formatted_loan(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_migration_restart_does_not_replace_persisted_records():
    LoanRecord.objects.filter(pk='L1').update(member='preserved')

    call_command('migrate', verbosity=0, interactive=False)

    assert GetLoan(DjangoLoanRepository()).execute('L1').member == 'preserved'


@pytest.mark.django_db
def test_seeded_loans_are_available_through_list_use_case():
    loans = ListLoans(DjangoLoanRepository()).execute()

    assert [loan.id for loan in loans] == ['L1', 'L2', 'L3']
    assert [loan.member for loan in loans] == ['ana', 'bo', 'cy']


@pytest.mark.django_db
def test_save_use_case_rolls_back_a_failed_transaction():
    repository = DjangoLoanRepository()

    with pytest.raises(IntegrityError):
        SaveLoan(repository).execute(Loan('L9', None, '123', date(2026, 3, 1), None))

    with pytest.raises(LoanNotFound):
        GetLoan(repository).execute('L9')


@pytest.mark.django_db
def test_save_use_case_persists_a_loan():
    repository = DjangoLoanRepository()
    loan = Loan('L9', 'dee', '123', date(2026, 3, 1), None)

    saved = SaveLoan(repository).execute(loan)

    assert GetLoan(repository).execute('L9') == saved


@pytest.mark.django_db
def test_htmx_unknown_loan_renders_the_catalog_error_fragment(client):
    response = client.get('/ui/loans/missing/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'No loan was found.' in response.content
    assert b'<!doctype html>' not in response.content


@pytest.mark.django_db
def test_htmx_loan_detail_renders_a_fragment(client):
    response = client.get('/ui/loans/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'Loan details' in response.content
    assert b'9780134685991' in response.content
    assert b'<!doctype html>' not in response.content


@pytest.mark.django_db
def test_catalog_page_lists_seeded_loans_and_detail_links(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'ana' in response.content
    assert b'hx-get="/ui/loans/L1/"' in response.content


@pytest.mark.django_db
def test_regular_loan_detail_renders_the_selected_loan(client):
    response = client.get('/ui/loans/L1/')

    assert response.status_code == 200
    assert b'Loan details' in response.content
    assert b'9780134685991' in response.content


@pytest.mark.django_db
def test_regular_unknown_loan_renders_a_404_page(client):
    response = client.get('/ui/loans/missing/')

    assert response.status_code == 404
    assert b'No loan was found.' in response.content
    assert b'<!doctype html>' in response.content


@pytest.mark.django_db
def test_unreturned_loan_date_is_nullable_in_storage():
    assert LoanRecord._meta.get_field('returned_on').null is True
