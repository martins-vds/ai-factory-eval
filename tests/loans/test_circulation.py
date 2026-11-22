from datetime import date
from types import SimpleNamespace

import pytest

from src.loans.services import (
    InvalidLoan,
    LendBook,
    LoanAlreadyReturned,
    LoanNotFound,
    ReturnBook,
)


class LoanRepository:
    def __init__(self):
        self.lend_calls = []
        self.loan = None
        self.return_calls = []

    def lend(self, member, isbn, lent_on):
        self.lend_calls.append((member, isbn, lent_on))
        return "created loan"

    def find(self, loan_id):
        return self.loan

    def mark_returned(self, loan_id, returned_on):
        self.return_calls.append((loan_id, returned_on))
        self.loan.returned_on = returned_on
        return self.loan


class FrozenClock:
    def today(self):
        return date(2026, 11, 22)


@pytest.mark.parametrize(
    ("member", "isbn", "field", "message"),
    [
        ("  ", "123", "member", "Enter a member name; blank values are not accepted."),
        ("reader", "\t", "isbn", "Enter an ISBN; blank values are not accepted."),
    ],
)
def test_lending_use_case_rejects_blank_fields(member, isbn, field, message):
    repository = LoanRepository()
    use_case = LendBook(repository, FrozenClock())

    with pytest.raises(InvalidLoan) as error:
        use_case.execute(member=member, isbn=isbn)

    assert error.value.errors == {field: message}
    assert repository.lend_calls == []


def test_lending_use_case_keeps_values_and_uses_clock_date():
    repository = LoanRepository()
    use_case = LendBook(repository, FrozenClock())

    loan = use_case.execute(member="  reader  ", isbn="123")

    assert loan == "created loan"
    assert repository.lend_calls == [
        ("  reader  ", "123", date(2026, 11, 22)),
    ]


def test_return_use_case_sets_date_from_clock():
    repository = LoanRepository()
    repository.loan = SimpleNamespace(returned_on=None)
    use_case = ReturnBook(repository, FrozenClock())

    loan = use_case.execute("L7")

    assert loan.returned_on == date(2026, 11, 22)
    assert repository.return_calls == [("L7", date(2026, 11, 22))]


def test_return_use_case_rejects_repeat_without_replacing_date():
    original_date = date(2026, 1, 15)
    repository = LoanRepository()
    repository.loan = SimpleNamespace(returned_on=original_date)
    use_case = ReturnBook(repository, FrozenClock())

    with pytest.raises(LoanAlreadyReturned):
        use_case.execute("L7")

    assert repository.loan.returned_on == original_date
    assert repository.return_calls == []


def test_return_use_case_rejects_unknown_loan():
    use_case = ReturnBook(LoanRepository(), FrozenClock())

    with pytest.raises(LoanNotFound):
        use_case.execute("missing")
