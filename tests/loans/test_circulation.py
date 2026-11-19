from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_a_loan_with_a_fourteen_day_due_date(client):
    today = date.today()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'


@pytest.mark.parametrize(
    'fields',
    [
        {},
        {'member': 'dee'},
        {'isbn': '123'},
        {'member': '', 'isbn': '123'},
        {'member': 'dee', 'isbn': ''},
        {'member': '  ', 'isbn': '123'},
        {'member': 'dee', 'isbn': '  '},
    ],
)
@pytest.mark.django_db
def test_lending_rejects_missing_or_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'


@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [
        ('  ', '123', 'member'),
        ('dee', '  ', 'isbn'),
    ],
)
def test_lending_use_case_rejects_blank_fields_without_using_the_store(member, isbn, field):
    from src.loans.services import LoanInputError, LoanService

    class Store:
        def lend(self, member, isbn, on):
            pytest.fail('invalid input must be rejected before persistence')

    with pytest.raises(LoanInputError) as error:
        LoanService(Store()).lend(member, isbn, date(2026, 3, 1))

    assert error.value.field_errors == {field: 'This field is required.'}


@pytest.mark.django_db
def test_return_endpoint_records_the_return_date(client):
    today = date.today()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today.isoformat()}\n'
    )
    assert Loan.objects.get(pk='L1').returned_on == today


def test_return_use_case_rejects_an_already_returned_loan_without_overwriting_its_date():
    from src.loans.services import LoanAlreadyReturned, LoanService

    first_return = date(2026, 3, 1)
    loan = SimpleNamespace(returned_on=first_return)

    class Store:
        def find(self, loan_id):
            return loan

        def mark_returned(self, loan_id, on):
            pytest.fail('a returned loan must not be changed')

    with pytest.raises(LoanAlreadyReturned):
        LoanService(Store()).mark_returned('L2', date(2026, 3, 2))

    assert loan.returned_on == first_return


@pytest.mark.django_db
def test_lending_endpoint_escapes_delimiters_quotes_and_line_breaks(client):
    today = date.today()

    response = client.post(
        '/loans',
        {'member': 'Reader; Example\nSecond line', 'isbn': '978"xyz'},
    )

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4;"Reader; Example\nSecond line";"978""xyz";'
        f'{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.django_db
def test_return_endpoint_rejects_repeat_without_replacing_original_date(client):
    original_return = date(2026, 1, 20)

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_return


@pytest.mark.django_db
def test_return_endpoint_returns_not_found_for_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_browser_lending_page_explains_the_form_fields(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'Lend a book' in response.content
    assert b'for="id_member"' in response.content
    assert b'for="id_isbn"' in response.content


@pytest.mark.django_db
def test_browser_can_lend_a_book_from_the_form(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '978123'},
    )

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'reader'
    assert loan.isbn == '978123'


@pytest.mark.django_db
def test_htmx_lending_redirects_to_the_collection_after_success(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '978123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/ui/loans/'
    assert Loan.objects.get(pk='L4').member == 'reader'


@pytest.mark.django_db
def test_browser_lending_page_shows_blank_field_errors(client):
    response = client.post('/ui/loans/new/', {'member': '', 'isbn': ''})

    assert response.status_code == 400
    assert b'This field is required.' in response.content
    assert b'id="id_member"' in response.content
    assert b'id="id_isbn"' in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_browser_lending_rejects_whitespace_only_fields(client):
    response = client.post('/ui/loans/new/', {'member': '  ', 'isbn': '123'})

    assert response.status_code == 400
    assert b'This field is required.' in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_htmx_lending_errors_render_the_form_again(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 400
    assert b'id="loan-form"' in response.content
    assert b'This field is required.' in response.content


@pytest.mark.django_db
def test_browser_catalog_offers_lending_and_return_actions(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'href="/ui/loans/new/"' in response.content
    assert b'hx-post="/ui/loans/L1/return/"' in response.content


@pytest.mark.django_db
def test_browser_can_return_a_loan_with_htmx(client):
    today = date.today()

    response = client.post(
        '/ui/loans/L1/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Returned' in response.content
    assert today.strftime('%b %-d, %Y').encode() in response.content
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_browser_repeat_return_shows_an_error_and_keeps_the_first_date(client):
    response = client.post(
        '/ui/loans/L2/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 409
    assert b'already been returned' in response.content
    assert Loan.objects.get(pk='L2').returned_on == date(2026, 1, 20)


@pytest.mark.django_db
def test_browser_return_page_renders_not_found_for_unknown_loan(client):
    response = client.post('/ui/loans/unknown/return/')

    assert response.status_code == 404
    assert b'No such loan' in response.content


@pytest.mark.django_db
def test_htmx_return_page_renders_not_found_for_unknown_loan(client):
    response = client.post(
        '/ui/loans/unknown/return/',
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 404
    assert b'No such loan' in response.content


@pytest.mark.django_db
def test_browser_return_route_accepts_only_post(client):
    response = client.get('/ui/loans/L1/return/')

    assert response.status_code == 405


@pytest.mark.django_db
def test_api_return_route_accepts_only_post(client):
    response = client.get('/loans/L1/return')

    assert response.status_code == 405


@pytest.mark.django_db
def test_api_lending_route_rejects_unsupported_methods(client):
    response = client.put('/loans', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 405


@pytest.mark.django_db
def test_browser_catalog_detail_renders_not_found_for_unknown_loan(client):
    response = client.get('/ui/loans/unknown/')

    assert response.status_code == 404
    assert b'No such loan' in response.content


def test_return_use_case_returns_none_for_an_unknown_loan():
    from src.loans.services import LoanService

    class Store:
        def find(self, loan_id):
            return None

        def mark_returned(self, loan_id, on):
            pytest.fail('an unknown loan must not be changed')

    assert LoanService(Store()).mark_returned('unknown', date(2026, 3, 1)) is None


def test_return_use_case_persists_the_supplied_date():
    from src.loans.services import LoanService

    loan = SimpleNamespace(returned_on=None)

    class Store:
        def find(self, loan_id):
            return loan

        def mark_returned(self, loan_id, on):
            loan.returned_on = on
            return loan

    returned = LoanService(Store()).mark_returned('L1', date(2026, 3, 1))

    assert returned.returned_on == date(2026, 3, 1)
