from datetime import date, timedelta

import pytest
from django.utils import timezone

from src.loans.services import LoanValidationError, lend_loan


class LoanStore:
    def __init__(self):
        self.created = []

    def next_id(self):
        return f'L{len(self.created) + 1}'

    def create(self, **fields):
        self.created.append(fields)
        return fields


@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [
        (' \t', '123', 'member'),
        ('reader', '\n ', 'isbn'),
    ],
)
def test_lend_use_case_rejects_blank_fields_without_creating_a_loan(member, isbn, field):
    store = LoanStore()

    with pytest.raises(LoanValidationError) as error:
        lend_loan(member, isbn, date(2026, 11, 18), store)

    assert error.value.errors == {field: 'This field is required.'}
    assert store.created == []


@pytest.mark.django_db
def test_lend_api_creates_a_loan_with_the_characterized_response(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})
    lent_on = timezone.localdate()

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.parametrize(
    'form',
    [
        {'member': 'reader'},
        {'member': '', 'isbn': '123'},
        {'member': ' \t ', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': 'reader', 'isbn': '\n'},
    ],
)
@pytest.mark.django_db
def test_lend_api_rejects_missing_or_blank_required_fields(client, form):
    response = client.post('/loans', form)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
