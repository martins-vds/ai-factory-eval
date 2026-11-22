from datetime import date

import pytest

from src.loans import services
from src.loans.models import Loan
from src.loans.repository import LoanRepository
from src.loans.services import LoanInputError


class FixedClock:
    def __init__(self, today):
        self._today = today

    def today(self):
        return self._today


@pytest.mark.django_db
def test_lending_creates_a_persisted_loan_with_a_fourteen_day_due_date():
    application = services.LoanApplication(
        LoanRepository(),
        FixedClock(date(2026, 3, 1)),
    )

    loan = application.lend('reader', '123')

    assert loan.id == 'L4'
    assert loan.lent_on == date(2026, 3, 1)
    assert loan.due_on == date(2026, 3, 15)
    assert Loan.objects.get(pk='L4') == loan


@pytest.mark.django_db
def test_lend_endpoint_returns_the_characterized_record(client, monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 3, 1))

    response = client.post('/loans', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L4;reader;123;2026-03-01;2026-03-15;\n'


@pytest.mark.django_db
def test_return_endpoint_persists_date_and_rejects_repeated_returns(client, monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 3, 1))

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'L1;ana;9780134685991;2026-01-02;2026-01-16;2026-03-01\n'

    repeated = client.post('/loans/L1/return')

    assert repeated.status_code == 409
    assert repeated.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 3, 1)


@pytest.mark.django_db
def test_return_endpoint_preserves_not_found_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [('', '123', 'member'), ('reader', '', 'isbn'), (' ', '123', 'member')],
)
@pytest.mark.django_db
def test_lending_rejects_blank_fields_through_the_use_case(member, isbn, field):
    application = services.LoanApplication(
        LoanRepository(),
        FixedClock(date(2026, 3, 1)),
    )
    existing_count = Loan.objects.count()

    with pytest.raises(LoanInputError) as error:
        application.lend(member, isbn)

    assert error.value.errors == {field: 'This field cannot be blank.'}
    assert Loan.objects.count() == existing_count


@pytest.mark.django_db
def test_repeated_return_is_rejected_without_replacing_the_first_return_date():
    first_return = services.LoanApplication(
        LoanRepository(),
        FixedClock(date(2026, 3, 1)),
    )
    later_return = services.LoanApplication(
        LoanRepository(),
        FixedClock(date(2026, 4, 1)),
    )

    loan = first_return.return_loan('L1')

    assert loan.returned_on == date(2026, 3, 1)
    with pytest.raises(ValueError, match='already returned'):
        later_return.return_loan('L1')
    assert Loan.objects.get(pk='L1').returned_on == date(2026, 3, 1)


@pytest.mark.django_db
def test_returning_an_unknown_loan_is_rejected_by_the_use_case():
    application = services.LoanApplication(
        LoanRepository(),
        FixedClock(date(2026, 3, 1)),
    )

    with pytest.raises(LookupError, match='no such loan'):
        application.return_loan('unknown')
