from datetime import date

import pytest

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_a_loan_with_a_fourteen_day_due_date(client):
    today = date.today()
    due_on = date.fromordinal(today.toordinal() + 14)

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == f'L4;dee;123;{today};{due_on};\n'
    loan = Loan.objects.get(pk='L4')
    assert loan.lent_on == today
    assert loan.due_on == due_on


@pytest.mark.parametrize(
    'form_data',
    [
        {},
        {'member': '', 'isbn': '123'},
        {'member': 'dee', 'isbn': ''},
        {'member': '  ', 'isbn': '123'},
        {'member': 'dee', 'isbn': '  '},
    ],
)
@pytest.mark.django_db
def test_lending_rejects_missing_or_blank_fields(client, form_data):
    response = client.post('/loans', form_data)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == 3
