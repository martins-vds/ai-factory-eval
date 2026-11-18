from datetime import date

import pytest

from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import LoanInputError, lend_loan


class FixedClock:
    def today(self):
        return date(2026, 11, 18)


@pytest.mark.parametrize(
    ('field', 'value'),
    [
        ('member', ''),
        ('member', ' \t'),
        ('isbn', ''),
        ('isbn', ' \t'),
    ],
)
def test_lend_use_case_rejects_blank_member_and_isbn(field, value):
    class Repository:
        def create(self, **fields):
            pytest.fail('invalid lending input must not be persisted')

    fields = {'member': 'reader', 'isbn': '123'}
    fields[field] = value

    with pytest.raises(LoanInputError) as error:
        lend_loan(fields['member'], fields['isbn'], Repository(), FixedClock())

    assert error.value.field_errors == {field: 'This field is required.'}


@pytest.mark.django_db
def test_lend_endpoint_creates_a_loan_with_a_fourteen_day_due_date(client, monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 11, 18))

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4;dee;123;2026-11-18;2026-12-02;\n'
    assert LoanRepository().find('L4').member == 'dee'
