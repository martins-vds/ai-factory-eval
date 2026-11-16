from datetime import date

import pytest
from django.urls import reverse

from src.loans.models import Loan
from src.loans.repository import save_loan


def test_catalog_routes_preserve_the_public_paths():
    assert reverse('loan-list') == '/loans'
    assert reverse('loan-detail', kwargs={'loan_id': 'L1'}) == '/loans/L1'
    assert reverse('ui-loan-list') == '/ui/loans/'
    assert reverse('ui-loan-detail', kwargs={'loan_id': 'L1'}) == '/ui/loans/L1/'


@pytest.mark.django_db
def test_list_returns_seed_loans_in_source_order_and_text_format(client):
    response = client.get(reverse('loan-list'))

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_get_returns_one_loan_with_due_date_and_trailing_newline(client):
    response = client.get(reverse('loan-detail', kwargs={'loan_id': 'L1'}))

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_get_returns_source_not_found_response_for_unknown_loan(client):
    response = client.get(reverse('loan-detail', kwargs={'loan_id': 'unknown'}))

    assert response.status_code == 404
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == 'no such loan\n'


def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan(id='L10', lent_on=date(2026, 1, 2))

    assert loan.due_on == date(2026, 1, 16)


@pytest.mark.django_db
def test_list_escapes_delimiters_and_line_breaks_in_exported_fields(client):
    save_loan(
        Loan(
            id='L4',
            member='a;"b',
            isbn='123\n456',
            lent_on=date(2026, 1, 1),
        )
    )

    response = client.get(reverse('loan-list'))

    assert response.status_code == 200
    assert response.content.decode().endswith('L4;"a;""b";"123\n456";2026-01-01;2026-01-15;\n')


@pytest.mark.django_db
def test_saved_loan_is_available_to_later_api_requests(client):
    loan = Loan.objects.get(pk='L1')
    loan.member = 'updated member'
    save_loan(loan)

    response = client.get(reverse('loan-detail', kwargs={'loan_id': 'L1'}))

    assert response.status_code == 200
    assert response.content.decode() == ('L1;updated member;9780134685991;2026-01-02;2026-01-16;\n')


@pytest.mark.django_db
def test_admin_login_route_is_not_available(client):
    assert client.get('/admin/login/').status_code == 404


@pytest.mark.django_db
def test_ui_loan_page_displays_the_catalog_record(client):
    response = client.get(reverse('ui-loan-detail', kwargs={'loan_id': 'L1'}))

    assert response.status_code == 200
    assert b'Loan L1' in response.content
    assert b'ana' in response.content
    assert b'9780134685991' in response.content


@pytest.mark.django_db
def test_loan_id_longer_than_thirty_two_characters_is_preserved(client):
    loan_id = f'L{"x" * 40}'
    save_loan(
        Loan(
            id=loan_id,
            member='member',
            isbn='isbn',
            lent_on=date(2026, 1, 1),
        )
    )

    response = client.get(reverse('loan-detail', kwargs={'loan_id': loan_id}))

    assert response.status_code == 200
    assert response.content.decode() == f'{loan_id};member;isbn;2026-01-01;2026-01-15;\n'


def test_unreturned_loan_date_is_optional_in_the_model():
    returned_on = Loan._meta.get_field('returned_on')

    assert returned_on.null
    assert returned_on.blank


@pytest.mark.django_db
def test_ui_catalog_renders_the_seed_records(client):
    response = client.get(reverse('ui-loan-list'))

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'9780134685991' in response.content
