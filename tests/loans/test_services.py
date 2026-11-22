from datetime import date

import pytest

from src.loans.domain import Loan
from src.loans.repository import DjangoLoanRepository
from src.loans.services import LoanCatalog


@pytest.mark.django_db
def test_catalog_use_case_returns_the_seed_records_in_id_order():
    catalog = LoanCatalog(DjangoLoanRepository())

    assert [
        (loan.id, loan.member, loan.isbn, loan.lent_on, loan.returned_on) for loan in catalog.all()
    ] == [
        ('L1', 'ana', '9780134685991', date(2026, 1, 2), None),
        ('L2', 'bo', '9780596007126', date(2026, 1, 10), date(2026, 1, 20)),
        ('L3', 'cy', '9781617294945', date(2025, 12, 1), date(2026, 1, 3)),
    ]


@pytest.mark.django_db
def test_catalog_use_case_returns_no_loan_for_an_unknown_identifier():
    catalog = LoanCatalog(DjangoLoanRepository())

    assert catalog.get('unknown') is None


def test_due_date_is_fourteen_calendar_days_after_lending():
    loan = Loan('L1', 'ana', '9780134685991', date(2026, 1, 2))

    assert loan.due_on == date(2026, 1, 16)


def test_text_export_escapes_semicolon_delimiters():
    loan = Loan('L6', 'a;b', '123;456', date(2026, 1, 2))

    assert LoanCatalog.text_line(loan) == ('L6;"a;b";"123;456";2026-01-02;2026-01-16;')


def test_text_export_escapes_quotes_and_line_breaks():
    loan = Loan('L7', 'a;\n"b', '123', date(2026, 1, 2))

    assert LoanCatalog.text_line(loan) == 'L7;"a;\n""b";123;2026-01-02;2026-01-16;'
