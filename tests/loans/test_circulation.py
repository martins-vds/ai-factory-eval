from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from django.test import Client
from django.utils import timezone

from src.loans.models import Loan
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
        self.concurrent_return_date = None

    def lend(self, member, isbn, lent_on):
        self.lend_calls.append((member, isbn, lent_on))
        return 'created loan'

    def find(self, loan_id):
        return self.loan

    def mark_returned(self, loan_id, returned_on):
        self.return_calls.append((loan_id, returned_on))
        if self.concurrent_return_date is not None:
            self.loan.returned_on = self.concurrent_return_date
            return None
        self.loan.returned_on = returned_on
        return self.loan


class FrozenClock:
    def today(self):
        return date(2026, 11, 22)


@pytest.mark.parametrize(
    ('member', 'isbn', 'field', 'message'),
    [
        (None, '123', 'member', 'Enter a member name; blank values are not accepted.'),
        ('  ', '123', 'member', 'Enter a member name; blank values are not accepted.'),
        ('reader', None, 'isbn', 'Enter an ISBN; blank values are not accepted.'),
        ('reader', '', 'isbn', 'Enter an ISBN; blank values are not accepted.'),
        ('reader', '\t', 'isbn', 'Enter an ISBN; blank values are not accepted.'),
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

    loan = use_case.execute(member='  reader  ', isbn='123')

    assert loan == 'created loan'
    assert repository.lend_calls == [
        ('  reader  ', '123', date(2026, 11, 22)),
    ]


def test_return_use_case_sets_date_from_clock():
    repository = LoanRepository()
    repository.loan = SimpleNamespace(returned_on=None)
    use_case = ReturnBook(repository, FrozenClock())

    loan = use_case.execute('L7')

    assert loan.returned_on == date(2026, 11, 22)
    assert repository.return_calls == [('L7', date(2026, 11, 22))]


def test_return_use_case_rejects_repeat_without_replacing_date():
    original_date = date(2026, 1, 15)
    repository = LoanRepository()
    repository.loan = SimpleNamespace(returned_on=original_date)
    use_case = ReturnBook(repository, FrozenClock())

    with pytest.raises(LoanAlreadyReturned):
        use_case.execute('L7')

    assert repository.loan.returned_on == original_date
    assert repository.return_calls == []


def test_return_use_case_preserves_date_when_another_return_wins_the_race():
    concurrent_date = date(2026, 11, 20)
    repository = LoanRepository()
    repository.loan = SimpleNamespace(returned_on=None)
    repository.concurrent_return_date = concurrent_date
    use_case = ReturnBook(repository, FrozenClock())

    with pytest.raises(LoanAlreadyReturned) as error:
        use_case.execute('L7')

    assert error.value.loan.returned_on == concurrent_date


def test_return_use_case_rejects_unknown_loan():
    use_case = ReturnBook(LoanRepository(), FrozenClock())

    with pytest.raises(LoanNotFound):
        use_case.execute('missing')


@pytest.mark.django_db
def test_api_lending_creates_and_returns_the_formatted_loan(client):
    today = timezone.localdate()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )
    assert Loan.objects.get(pk='L4').member == 'dee'


@pytest.mark.parametrize(
    'fields',
    [
        {},
        {'member': 'reader'},
        {'isbn': '123'},
        {'member': '', 'isbn': '123'},
        {'member': '  ', 'isbn': '123'},
        {'member': 'reader', 'isbn': '\t'},
    ],
)
@pytest.mark.django_db
def test_api_lending_rejects_missing_and_blank_fields(client, fields):
    count = Loan.objects.count()

    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == count


@pytest.mark.django_db
def test_api_return_records_date_and_rejects_repeated_return(client):
    today = timezone.localdate()

    first_response = client.post('/loans/L1/return')

    assert first_response.status_code == 200
    assert first_response['Content-Type'] == 'text/plain'
    assert first_response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today.isoformat()}\n'
    )
    assert Loan.objects.get(pk='L1').returned_on == today

    repeated_response = client.post('/loans/L1/return')

    assert repeated_response.status_code == 409
    assert repeated_response['Content-Type'] == 'text/plain'
    assert repeated_response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_api_return_rejects_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_api_return_only_accepts_post(client):
    response = client.get('/loans/L1/return')

    assert response.status_code == 405
    assert Loan.objects.get(pk='L1').returned_on is None


@pytest.mark.django_db
def test_browser_can_open_the_reading_room_lending_form(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'Lend a book' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content
    assert response.content.count(b'value=""') == 2


@pytest.mark.django_db
def test_reading_room_catalog_offers_lend_and_return_actions(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'href="/ui/loans/new/"' in response.content
    assert b'hx-post="/ui/loans/L1/return/"' in response.content
    assert b'Return book' in response.content


@pytest.mark.parametrize('headers', [{}, {'HTTP_HX_REQUEST': 'true'}])
@pytest.mark.django_db
def test_browser_lending_shows_field_errors_and_keeps_entered_values(client, headers):
    response = client.post(
        '/ui/loans/',
        {'member': '  ', 'isbn': '\t'},
        **headers,
    )

    assert response.status_code == 400
    assert b'Enter a member name; blank values are not accepted.' in response.content
    assert b'Enter an ISBN; blank values are not accepted.' in response.content
    assert b'value="  "' in response.content
    assert b'value="\t"' in response.content


@pytest.mark.django_db
def test_browser_lending_creates_a_loan_then_redirects_to_collection(client):
    today = timezone.localdate()

    response = client.post('/ui/loans/', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'reader'
    assert loan.isbn == '123'
    assert loan.lent_on == today
    assert loan.due_on == today + timedelta(days=14)


@pytest.mark.django_db
def test_htmx_lending_redirects_to_collection(client):
    response = client.post(
        '/ui/loans/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/ui/loans/'
    assert Loan.objects.get(pk='L4').member == 'reader'


@pytest.mark.django_db
def test_browser_return_updates_row_and_repeat_keeps_original_date(client):
    today = timezone.localdate()

    response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert f'Returned {today.strftime("%b")} {today.day}, {today.year}'.encode() in response.content
    assert b'Return book' not in response.content
    assert Loan.objects.get(pk='L1').returned_on == today

    repeated = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert repeated.status_code == 409
    assert b'original date remains on record' in repeated.content
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_browser_return_without_htmx_redirects_to_collection(client):
    today = timezone.localdate()

    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_browser_repeat_return_keeps_a_preexisting_return_date(client):
    response = client.post(
        '/ui/loans/L2/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 409
    assert b'Returned Jan 20, 2026' in response.content
    assert Loan.objects.get(pk='L2').returned_on == date(2026, 1, 20)


@pytest.mark.django_db
def test_browser_return_unknown_loan_shows_error(client):
    response = client.post('/ui/loans/missing/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'No such loan.' in response.content


@pytest.mark.django_db
def test_browser_return_only_accepts_post(client):
    response = client.get('/ui/loans/L1/return/')

    assert response.status_code == 405
    assert Loan.objects.get(pk='L1').returned_on is None


@pytest.mark.django_db
def test_legacy_api_posts_do_not_require_browser_csrf_tokens():
    client = Client(enforce_csrf_checks=True)

    lending = client.post('/loans', {'member': 'reader', 'isbn': '123'})

    assert lending.status_code == 201
    returned = client.post('/loans/L4/return')
    assert returned.status_code == 200

    browser_post = client.post('/ui/loans/', {'member': 'another', 'isbn': '456'})
    assert browser_post.status_code == 403
