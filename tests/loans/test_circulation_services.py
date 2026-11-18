from datetime import date, timedelta

import pytest

from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import InvalidLoan, LoanAlreadyReturned, lend_loan, return_loan


@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [(None, '123', 'member'), ('reader', None, 'isbn')],
)
@pytest.mark.django_db
def test_lend_loan_rejects_missing_required_values(member, isbn, field):
    with pytest.raises(InvalidLoan) as error:
        lend_loan(LoanRepository(), member, isbn, date.today())

    assert set(error.value.errors) == {field}


@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [(' ', '123', 'member'), ('reader', '\t', 'isbn')],
)
@pytest.mark.django_db
def test_lend_loan_rejects_blank_values(member, isbn, field):
    with pytest.raises(InvalidLoan) as error:
        lend_loan(LoanRepository(), member, isbn, date.today())

    assert set(error.value.errors) == {field}


@pytest.mark.django_db
def test_lend_loan_records_the_server_date():
    today = date.today()

    loan = lend_loan(LoanRepository(), 'reader', '123', today)

    assert loan.lent_on == today


@pytest.mark.django_db
def test_lend_loan_sets_due_date_fourteen_days_after_lending():
    lent_on = date(2026, 3, 1)

    loan = lend_loan(LoanRepository(), 'reader', '123', lent_on)

    assert loan.due_on == lent_on + timedelta(days=14)


@pytest.mark.django_db
def test_lend_loan_allocates_an_id_after_the_existing_loan_count():
    next_id = f'L{Loan.objects.count() + 1}'

    loan = lend_loan(LoanRepository(), 'reader', '123', date.today())

    assert loan.id == next_id


@pytest.mark.django_db
def test_return_loan_records_the_server_date():
    today = date.today()

    loan = return_loan(LoanRepository(), 'L1', today)

    assert loan.returned_on == today
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_return_loan_reports_an_unknown_id():
    assert return_loan(LoanRepository(), 'unknown', date.today()) is None


@pytest.mark.django_db
def test_return_loan_rejects_a_repeat_without_changing_the_date():
    original_date = Loan.objects.get(pk='L2').returned_on

    with pytest.raises(LoanAlreadyReturned):
        return_loan(LoanRepository(), 'L2', date.today())

    assert Loan.objects.get(pk='L2').returned_on == original_date
