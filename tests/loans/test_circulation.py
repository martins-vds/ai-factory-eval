from datetime import date, timedelta

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.loans.models import Loan
from src.loans.services import InvalidLoan, LoanUseCases


class LoanRecorder:
    def __init__(self):
        self.requests = []

    def lend(self, member, isbn, lent_on):
        self.requests.append((member, isbn, lent_on))


class FixedClock:
    def today(self):
        return date(2026, 11, 18)


@pytest.mark.django_db
def test_lend_endpoint_creates_a_loan_with_a_fourteen_day_due_date(client):
    today = timezone.localdate()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )
    loan = Loan.objects.get(pk='L4')
    assert loan.lent_on == today
    assert loan.due_on == today + timedelta(days=14)


@pytest.mark.parametrize(
    'fields',
    [
        {},
        {'member': '', 'isbn': '123'},
        {'member': '   ', 'isbn': '123'},
        {'member': 'dee', 'isbn': ''},
        {'member': 'dee', 'isbn': '   '},
    ],
)
@pytest.mark.django_db
def test_lend_endpoint_rejects_missing_or_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'member and isbn are required\n'
    assert Loan.objects.count() == 3


@pytest.mark.parametrize(
    ('member', 'isbn', 'expected_fields'),
    [
        ('   ', '123', {'member': 'This field is required.'}),
        ('reader', '   ', {'isbn': 'This field is required.'}),
        (
            '   ',
            '   ',
            {
                'member': 'This field is required.',
                'isbn': 'This field is required.',
            },
        ),
    ],
)
def test_lend_use_case_reports_each_blank_field_before_creating_a_loan(
    member, isbn, expected_fields
):
    repository = LoanRecorder()
    use_cases = LoanUseCases(repository, FixedClock())

    with pytest.raises(InvalidLoan) as error:
        use_cases.lend(member, isbn)

    assert error.value.fields == expected_fields
    assert repository.requests == []


@pytest.mark.django_db
def test_return_endpoint_persists_the_return_date(client):
    today = timezone.localdate()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode().endswith(f';{today.isoformat()}\n')
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_return_endpoint_rejects_unknown_loans(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'


@pytest.mark.django_db
def test_return_endpoint_rejects_a_repeat_without_replacing_the_date(client):
    original_return_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_return_date


@pytest.mark.django_db
def test_lending_page_uses_the_reading_room_form_and_ui_route(client):
    response = client.get('/ui/loans/new/')

    assert response.status_code == 200
    assert b'Lend a book' in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content
    assert b'action="/ui/loans/"' in response.content
    assert b'hx-post="/ui/loans/"' in response.content
    assert response.content.count(b'class="input input-bordered w-full"') == 2


@pytest.mark.django_db
def test_lending_page_shows_field_errors_for_blank_values(client):
    response = client.post('/ui/loans/new/', {'member': '', 'isbn': ' '})

    assert response.status_code == 200
    assert b'<!doctype html>' in response.content
    assert b'This field is required.' in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_browser_lending_creates_a_loan_and_redirects_to_its_record(client):
    response = client.post('/ui/loans/', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'
    assert Loan.objects.get(pk='L4').member == 'dee'


@pytest.mark.django_db
def test_loan_list_page_displays_the_collection_and_lend_link(client):
    response = client.get('/ui/loans/')

    assert response.status_code == 200
    assert b'Books in good company.' in response.content
    assert b'Loan L1' in response.content
    assert b'href="/ui/loans/new/"' in response.content


@pytest.mark.parametrize(
    'path',
    ['/ui/loans/', '/ui/loans/new/'],
)
@pytest.mark.django_db
def test_lending_pages_reject_unsupported_methods(client, path):
    response = client.put(path)

    assert response.status_code == 405


@pytest.mark.django_db
def test_htmx_lending_returns_a_created_loan_fragment(client):
    response = client.post(
        '/ui/loans/',
        {'member': 'dee', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 201
    assert b'role="status"' in response.content
    assert b'Loan L4 has been recorded.' in response.content
    assert b'href="/ui/loans/L4/"' in response.content


@pytest.mark.django_db
def test_htmx_lending_validation_returns_only_the_form_fragment(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '', 'isbn': ' '},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'<!doctype html>' not in response.content
    assert b'name="member"' in response.content
    assert b'name="isbn"' in response.content
    assert response.content.count(b'This field is required.') == 2


@pytest.mark.django_db
def test_browser_return_page_returns_not_found_for_unknown_loan(client):
    response = client.post('/ui/loans/unknown/return/')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'


@pytest.mark.django_db
def test_browser_repeat_return_shows_original_date_and_preserves_it(client):
    original_return_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/ui/loans/L2/return/')

    assert response.status_code == 409
    assert b'role="alert"' in response.content
    assert b'already been returned' in response.content
    assert b'Jan 20, 2026' in response.content
    assert Loan.objects.get(pk='L2').returned_on == original_return_date


@pytest.mark.django_db
def test_htmx_repeat_return_renders_a_swappable_status(client):
    original_return_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/ui/loans/L2/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'already been returned' in response.content
    assert b'Loan L2' in response.content
    assert b'Jan 20, 2026' in response.content
    assert Loan.objects.get(pk='L2').returned_on == original_return_date


@pytest.mark.parametrize(
    'path',
    ['/loans', '/loans/L1/return', '/ui/loans/', '/ui/loans/new/', '/ui/loans/L1/return/'],
)
@pytest.mark.django_db
def test_loan_endpoints_reject_unsupported_methods(client, path):
    response = client.put(path)

    assert response.status_code == 405


@pytest.mark.django_db
def test_browser_return_redirects_to_the_updated_record(client):
    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L1/'
    assert Loan.objects.get(pk='L1').returned_on == timezone.localdate()


@pytest.mark.django_db
def test_htmx_return_reports_the_successful_transition(client):
    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'role="status"' in response.content
    assert b'Loan L1 was marked returned on' in response.content
    assert Loan.objects.get(pk='L1').returned_on == timezone.localdate()


@pytest.mark.django_db(transaction=True)
def test_return_endpoint_saves_outside_a_test_transaction(client):
    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert Loan.objects.get(pk='L1').returned_on == timezone.localdate()


@pytest.mark.django_db(transaction=True)
def test_real_browser_can_lend_and_return_a_book(live_server):
    today = timezone.localdate()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            context = browser.new_context(java_script_enabled=False)
            page = context.new_page()
            page.goto(f'{live_server.url}/ui/loans/new/')
            page.get_by_label('Member').fill('dee')
            page.get_by_label('ISBN').fill('123')
            page.get_by_role('button', name='Record this loan').click()
            assert page.url.endswith('/ui/loans/L4/')
            page.get_by_role('button', name='Mark as returned').click()
            assert page.locator('dd').nth(2).inner_text() == (
                f'{today.strftime("%b")} {today.day}, {today.year}'
            )
        finally:
            context.close()
            browser.close()

    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.returned_on == today
