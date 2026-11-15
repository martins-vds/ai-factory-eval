from datetime import timedelta

import pytest
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_api_creates_a_formatted_loan_with_a_fourteen_day_due_date(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})
    lent_on = timezone.localdate()

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};'
        f'{(lent_on + timedelta(days=14)).isoformat()};\n'
    )
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.lent_on == lent_on


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fields',
    [
        {},
        {'member': '', 'isbn': '123'},
        {'member': '   ', 'isbn': '123'},
        {'member': 'reader', 'isbn': '\t '},
    ],
)
def test_lending_api_rejects_missing_or_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_lending_api_escapes_delimiters_in_the_created_loan(client):
    response = client.post('/loans', {'member': 'a;b', 'isbn': '123;456'})

    assert response.status_code == 201
    assert response.content.decode().startswith('L4;"a;b";"123;456";')


@pytest.mark.django_db
def test_return_api_marks_a_loan_returned(client):
    response = client.post('/loans/L1/return')
    loan = Loan.objects.get(pk='L1')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert loan.returned_on == timezone.localdate()
    assert response.content.decode().endswith(f'{loan.returned_on.isoformat()}\n')


@pytest.mark.django_db
def test_return_api_returns_not_found_for_an_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_repeated_return_is_rejected_without_changing_the_original_date(client):
    original_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_browser_lending_form_uses_ui_htmx_path_and_shows_field_errors(client):
    page = client.get('/ui/loans/new/')
    response = client.post(
        '/ui/loans/new/',
        {'member': '  ', 'isbn': ''},
        HTTP_HX_REQUEST='true',
    )

    assert page.status_code == 200
    assert b'hx-post="/ui/loans/new/"' in page.content
    assert response.status_code == 200
    assert b'Member' in response.content
    assert b'ISBN' in response.content
    assert response.content.count(b'This field is required.') == 2
    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_browser_lending_form_creates_a_loan_and_returns_an_htmx_confirmation(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert b'Loan L4 is now in the collection.' in response.content
    assert b'href="/ui/loans/L4/"' in response.content
    assert Loan.objects.filter(pk='L4', member='dee', isbn='123').exists()


@pytest.mark.django_db
def test_browser_return_uses_ui_htmx_path_and_preserves_return_date(client):
    page = client.get('/ui/loans/L1/')

    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')
    returned_on = Loan.objects.get(pk='L1').returned_on
    repeated = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert b'hx-post="/ui/loans/L1/return/"' in page.content
    assert response.status_code == 200
    assert b'This loan was returned' in response.content
    assert repeated.status_code == 200
    assert b'already returned' in repeated.content
    assert Loan.objects.get(pk='L1').returned_on == returned_on


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_browser_can_lend_and_return_a_book_through_htmx(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/loans/new/')
            page.get_by_label('Member').fill('reader')
            page.get_by_label('ISBN').fill('123')
            page.get_by_role('button', name='Lend this book').click()
            page.wait_for_function(
                "() => location.pathname.endsWith('/ui/loans/L4/') || "
                "document.body.innerText.includes('Loan L4 is now in the collection.')",
                timeout=5000,
            )

            page.goto(f'{live_server.url}/ui/loans/L4/')
            page.get_by_role('button', name='Mark as returned').click()
            page.get_by_text('This loan was returned on').wait_for(timeout=5000)
        finally:
            browser.close()
