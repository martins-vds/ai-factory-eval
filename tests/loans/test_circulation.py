from datetime import date, timedelta

import pytest

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_endpoint_creates_a_loan_with_the_characterized_record(client):
    lent_on = date.today()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.lent_on == lent_on
