from datetime import date, timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import LoanAlreadyReturned, LoanInputError, lend_loan, return_loan


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('member', 'isbn', 'invalid_field'),
    [
        (None, '123', 'member'),
        (' \t', '123', 'member'),
        ('reader', None, 'isbn'),
        ('reader', ' \t', 'isbn'),
    ],
)
def test_lending_rejects_missing_or_blank_fields(member, isbn, invalid_field):
    loan_count = LoanRepository().all().count()

    with pytest.raises(LoanInputError) as error:
        lend_loan(
            repository=LoanRepository(),
            member=member,
            isbn=isbn,
            lent_on=date(2026, 11, 19),
        )

    assert error.value.fields == {invalid_field: 'This field is required.'}
    assert LoanRepository().all().count() == loan_count


@pytest.mark.django_db
def test_lending_endpoint_creates_a_loan_and_escapes_delimiters(client):
    today = timezone.localdate()
    response = client.post(
        '/loans',
        {'member': 'Reader; Example', 'isbn': '123;456'},
    )

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;"Reader; Example";"123;456";{today.isoformat()};'
        f'{(today + timedelta(days=14)).isoformat()};\n'
    )
    loan = Loan.objects.get(pk='L4')
    assert (loan.member, loan.isbn, loan.lent_on) == (
        'Reader; Example',
        '123;456',
        today,
    )


@pytest.mark.django_db
def test_return_use_case_rejects_repeated_return_without_changing_the_date():
    original_date = Loan.objects.get(pk='L2').returned_on

    with pytest.raises(LoanAlreadyReturned):
        return_loan(
            repository=LoanRepository(),
            loan_id='L2',
            returned_on=date(2026, 11, 19),
        )

    assert Loan.objects.get(pk='L2').returned_on == original_date
