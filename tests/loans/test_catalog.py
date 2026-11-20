from datetime import date

import pytest

from src.loans.domain import Loan
from src.loans.services import calculate_due_date, export_loans, get_loan, list_loans

SEED_EXPORT = (
    'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    'L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n'
)


@pytest.mark.django_db
def test_list_returns_seeded_loans_in_characterized_format(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == SEED_EXPORT


@pytest.mark.django_db
def test_get_returns_one_loan_with_trailing_newline(client):
    response = client.get('/loans/L1')

    assert response.status_code == 200
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'


@pytest.mark.django_db
def test_get_missing_loan_returns_characterized_not_found_response(client):
    response = client.get('/loans/missing')

    assert response.status_code == 404
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_ui_missing_loan_renders_an_htmx_error_fragment(client):
    response = client.get('/ui/loans/missing/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_ui_htmx_detail_returns_a_record_fragment(client):
    response = client.get('/ui/loans/L1/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'Loan L1' in response.content
    assert b'9780134685991' in response.content


@pytest.mark.django_db
def test_django_admin_is_not_available(client):
    assert client.get('/admin/login/').status_code == 404


def test_due_date_is_fourteen_calendar_days_after_lending():
    assert calculate_due_date(date(2026, 1, 2)) == date(2026, 1, 16)


def test_list_use_case_orders_loans_by_identifier():
    later_loan = Loan('L3', 'cy', '9781617294945', date(2025, 12, 1), None)
    earlier_loan = Loan('L1', 'ana', '9780134685991', date(2026, 1, 2), None)

    class UnorderedRepository:
        def list_all(self):
            return [later_loan, earlier_loan]

    assert list_loans(UnorderedRepository()) == [earlier_loan, later_loan]


def test_get_use_case_returns_none_for_unknown_identifier():
    class EmptyRepository:
        def find_by_id(self, loan_id):
            return None

    assert get_loan(EmptyRepository(), 'missing') is None


def test_export_escapes_delimiters_and_quotes_in_field_values():
    loan = Loan(
        id='L4',
        member='a;b\nname',
        isbn='123"456',
        lent_on=date(2026, 1, 2),
        returned_on=None,
    )

    assert export_loans([loan]) == 'L4;"a;b\nname";"123""456";2026-01-02;2026-01-16;\n'
