import pytest

from src.loans.services import InvalidLoan, LendBook


class LoanRepository:
    def __init__(self):
        self.lend_calls = []

    def lend(self, member, isbn, lent_on):
        self.lend_calls.append((member, isbn, lent_on))


class FrozenClock:
    def today(self):
        return "2026-11-22"


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
