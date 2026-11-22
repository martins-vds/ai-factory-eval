from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from threading import Barrier

import pytest
from django.db import close_old_connections
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.loans.domain import Loan, LoanAlreadyReturned, LoanInputError, LoanNotFound
from src.loans.repository import LoanRepository
from src.loans.services import LoanApplication


class InMemoryLoanStore:
    def __init__(self, loans=()):
        self.loans = {loan.id: loan for loan in loans}

    def all(self):
        return list(self.loans.values())

    def find(self, loan_id):
        return self.loans.get(loan_id)

    def add(self, loan):
        self.loans[loan.id] = loan
        return loan

    def save_returned(self, loan):
        self.loans[loan.id] = loan
        return loan


class SynchronizedLoanStore:
    def __init__(self, repository, barrier):
        self.repository = repository
        self.barrier = barrier

    def lend(self, member, isbn, lent_on):
        self.barrier.wait(timeout=10)
        return self.repository.lend(member, isbn, lent_on)


@pytest.mark.django_db
def test_api_lends_a_book_and_returns_the_formatted_loan(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    today = timezone.localdate()
    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.parametrize(
    ('member', 'isbn', 'field'),
    [
        (None, '123', 'member'),
        ('', '123', 'member'),
        ('  ', '123', 'member'),
        ('reader', None, 'isbn'),
        ('reader', '', 'isbn'),
        ('reader', '  ', 'isbn'),
    ],
)
def test_lending_use_case_rejects_blank_required_fields(member, isbn, field):
    application = LoanApplication(InMemoryLoanStore())

    with pytest.raises(LoanInputError) as error:
        application.lend(member, isbn, date(2026, 3, 1))

    assert error.value.fields == {field: 'This field is required.'}


@pytest.mark.django_db
@pytest.mark.parametrize(
    'form',
    [
        {'isbn': '123'},
        {'member': 'reader'},
        {},
        {'member': '', 'isbn': '123'},
        {'member': 'reader', 'isbn': ''},
        {'member': '  ', 'isbn': '123'},
        {'member': 'reader', 'isbn': '  '},
    ],
)
def test_api_rejects_blank_required_fields(client, form):
    response = client.post('/loans', form)

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'


def test_return_use_case_rejects_an_unknown_loan():
    application = LoanApplication(InMemoryLoanStore())

    with pytest.raises(LoanNotFound):
        application.return_loan('unknown', date(2026, 3, 1))


def test_return_use_case_keeps_the_original_date_on_a_repeat_return():
    original_date = date(2026, 2, 20)
    loan = Loan('L1', 'reader', '123', date(2026, 2, 1), original_date)
    application = LoanApplication(InMemoryLoanStore([loan]))

    with pytest.raises(LoanAlreadyReturned):
        application.return_loan('L1', date(2026, 3, 1))

    assert loan.returned_on == original_date


@pytest.mark.django_db
def test_api_return_records_date_and_unknown_id_returns_not_found(client):
    returned = client.post('/loans/L1/return')
    unknown = client.post('/loans/unknown/return')

    assert returned.status_code == 200
    assert returned.content.decode().endswith(f'{timezone.localdate().isoformat()}\n')
    assert unknown.status_code == 404
    assert unknown.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_api_repeat_return_is_rejected_without_replacing_the_original_date(client):
    original_date = date(2026, 1, 20)
    application = LoanApplication(LoanRepository())

    repeated = client.post('/loans/L2/return')

    assert repeated.status_code == 409
    assert repeated.content.decode() == 'loan has already been returned\n'
    assert application.find_loan('L2').returned_on == original_date


@pytest.mark.django_db
def test_api_lending_escapes_field_and_record_delimiters(client):
    response = client.post(
        '/loans',
        {'member': 'Reader; Example\nSecond line', 'isbn': '978"xyz;123'},
    )

    today = timezone.localdate()
    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4;"Reader; Example\nSecond line";"978""xyz;123";{today.isoformat()};'
        f'{(today + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.django_db(transaction=True)
def test_concurrent_lending_assigns_distinct_loan_ids():
    barrier = Barrier(2)
    application = LoanApplication(SynchronizedLoanStore(LoanRepository(), barrier))

    def lend(member):
        close_old_connections()
        try:
            return application.lend(member, '123', date(2026, 3, 1))
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as workers:
        loans = list(workers.map(lend, ('reader one', 'reader two')))

    assert sorted(loan.id for loan in loans) == ['L4', 'L5']


@pytest.mark.django_db
def test_reading_room_has_a_lend_form(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'<h1' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content


@pytest.mark.django_db
def test_reading_room_lending_shows_field_errors_on_a_full_page(client):
    response = client.post('/ui/loans/new/', {'member': '  ', 'isbn': '123'})

    assert response.status_code == 400
    assert b'This field is required.' in response.content
    assert b'value="  "' in response.content
    assert LoanApplication(LoanRepository()).find_loan('L4') is None


@pytest.mark.django_db
def test_reading_room_lending_renders_htmx_validation_errors(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 400
    assert b'This field is required.' in response.content
    assert b'id="lend-form"' in response.content


@pytest.mark.django_db
def test_reading_room_lends_a_book_and_redirects_to_its_record(client):
    response = client.post('/ui/loans/new/', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'
    assert b'Loan L4' in client.get(response['Location']).content


@pytest.mark.django_db
def test_reading_room_return_renders_success_and_preserves_a_repeated_date(client):
    first = client.post('/ui/loans/L1/return/')
    repeated = client.post('/ui/loans/L2/return/')

    assert first.status_code == 302
    assert first['Location'] == '/ui/loans/L1/'
    assert repeated.status_code == 409
    assert b'This loan has already been returned.' in repeated.content
    assert b'Jan 20, 2026' in repeated.content


@pytest.mark.django_db
def test_reading_room_unknown_htmx_return_renders_an_error(client):
    fragment = client.post('/ui/loans/missing/return/', HTTP_HX_REQUEST='true')
    page = client.post('/ui/loans/missing/return/')

    assert fragment.status_code == 404
    assert b'No such loan' in fragment.content
    assert page.status_code == 404
    assert b'No such loan' in page.content


@pytest.mark.django_db
def test_reading_room_htmx_repeat_return_keeps_the_original_date(client):
    response = client.post('/ui/loans/L2/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 409
    assert b'Jan 20, 2026' in response.content


@pytest.mark.django_db
def test_htmx_lending_and_return_return_html_fragments(client):
    lent = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )
    returned = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert lent.status_code == 201
    assert b'Added to the collection' in lent.content
    assert returned.status_code == 200
    assert b'Returned ' in returned.content


@pytest.mark.django_db
def test_browser_can_lend_a_book(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.set_default_timeout(3000)
            page.goto(f'{live_server.url}/ui/loans/')
            htmx_loaded = page.evaluate('typeof window.htmx === "object"')
            page.get_by_role('link', name='Lend a book').click()
            page.get_by_label('Member').fill('reader')
            page.get_by_label('ISBN').fill('123')
            if htmx_loaded:
                with page.expect_response(
                    lambda response: (
                        response.url.endswith('/ui/loans/new/')
                        and response.request.method == 'POST'
                    )
                ) as post:
                    page.get_by_role('button', name='Lend book').click()
                response = post.value
                assert response.request.headers.get('hx-request') == 'true'
                assert response.status == 201
                assert page.get_by_role('link', name='View this loan').is_visible()
            else:
                page.get_by_role('button', name='Lend book').click()
                page.wait_for_url(f'{live_server.url}/ui/loans/L4/')

            page.get_by_role('button', name='Mark returned').click()
            if htmx_loaded:
                assert page.get_by_role('status').filter(has_text='Returned').is_visible()
            else:
                page.wait_for_load_state('networkidle')
                assert page.get_by_role('status').filter(has_text='Returned').is_visible()
        finally:
            browser.close()
