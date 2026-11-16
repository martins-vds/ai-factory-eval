from datetime import date

import pytest

from src.loans.models import Loan
from src.loans.repository import save_loan

@pytest.mark.django_db
def test_list_returns_seed_loans_in_source_order_and_text_format(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
        'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
    )


@pytest.mark.django_db
def test_get_returns_one_loan_with_due_date_and_trailing_newline(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_get_returns_source_not_found_response_for_unknown_loan(client):
    response = client.get('/loans/unknown')

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

    response = client.get('/loans')

    assert response.status_code == 200
    assert response.content.decode().endswith(
        'L4;"a;""b";"123\n456";2026-01-01;2026-01-15;\n'
    )


@pytest.mark.django_db
def test_saved_loan_is_available_to_later_api_requests(client):
    loan = Loan.objects.get(pk='L1')
    loan.member = 'updated member'
    save_loan(loan)

    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == (
        'L1;updated member;9780134685991;2026-01-02;2026-01-16;\n'
    )


@pytest.mark.django_db
def test_admin_login_route_is_not_available(client):
    assert client.get('/admin/login/').status_code == 404
