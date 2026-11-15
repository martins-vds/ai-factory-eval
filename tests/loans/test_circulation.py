from datetime import date, timedelta

import pytest
from django.test import Client
from django.utils import timezone
from playwright.sync_api import sync_playwright

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_and_returns_the_characterized_record(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.lent_on == timezone.localdate()
    assert loan.due_on == loan.lent_on + timedelta(days=14)
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{loan.lent_on.isoformat()};{loan.due_on.isoformat()};\n'
    )


@pytest.mark.django_db
def test_api_lending_preserves_source_fields_but_quotes_export_delimiters(client):
    response = client.post(
        '/loans',
        {'member': 'a;b', 'isbn': '123\n456'},
    )

    loan = Loan.objects.get(pk='L4')
    assert response.status_code == 201
    assert loan.member == 'a;b'
    assert loan.isbn == '123\n456'
    assert response.content.decode() == (
        f'L4;"a;b";"123\n456";{loan.lent_on.isoformat()};{loan.due_on.isoformat()};\n'
    )


@pytest.mark.django_db
def test_api_lending_does_not_require_a_browser_csrf_token():
    response = Client(enforce_csrf_checks=True).post(
        '/loans',
        {'member': 'dee', 'isbn': '123'},
    )

    assert response.status_code == 201


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fields',
    [
        {'member': 'dee'},
        {'isbn': '123'},
        {'member': '', 'isbn': '123'},
        {'member': 'dee', 'isbn': ''},
        {'member': '  ', 'isbn': '123'},
        {'member': 'dee', 'isbn': '\t'},
    ],
)
def test_lending_rejects_missing_or_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'
    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_browser_lending_form_shows_field_errors_for_blank_values(client):
    form_page = client.get('/ui/loans/new/')

    assert form_page.status_code == 200
    assert b'hx-post="/ui/loans/new/"' in form_page.content

    response = client.post('/ui/loans/new/', {'member': ' ', 'isbn': ''})

    assert response.status_code == 200
    assert response.context['form'].errors.keys() == {'member', 'isbn'}
    assert b'hx-post="/ui/loans/new/"' in response.content
    assert not Loan.objects.filter(pk='L4').exists()


@pytest.mark.django_db
def test_browser_lending_form_creates_a_loan_and_redirects_htmx(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'dee', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 200
    assert response['HX-Redirect'] == '/ui/loans/'
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'dee'
    assert loan.isbn == '123'
    assert loan.due_on == loan.lent_on + timedelta(days=14)


@pytest.mark.django_db
def test_return_updates_the_loan_and_rejects_a_repeat_without_changing_the_date(client):
    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    returned_on = Loan.objects.get(pk='L1').returned_on
    assert returned_on == timezone.localdate()
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )


@pytest.mark.django_db
def test_repeat_return_rejects_request_and_preserves_existing_date(client):
    repeated = client.post('/loans/L2/return')

    assert repeated.status_code == 409
    assert repeated['Content-Type'] == 'text/plain'
    assert repeated.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == date(2026, 1, 20)


@pytest.mark.django_db
def test_return_reports_unknown_loan(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_browser_return_uses_htmx_and_updates_the_detail_page(client):
    detail = client.get('/ui/loans/L1/')

    assert detail.status_code == 200
    assert b'hx-post="/ui/loans/L1/return/"' in detail.content

    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert response['HX-Redirect'] == '/ui/loans/L1/'
    assert Loan.objects.get(pk='L1').returned_on == timezone.localdate()


@pytest.mark.django_db
def test_browser_can_lend_and_return_a_book(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/loans/new/')
            page.get_by_label('Member').fill('reader')
            page.get_by_label('ISBN').fill('123')
            page.get_by_role('button', name='Lend this book').click()

            page.wait_for_url(f'{live_server.url}/ui/loans/')
            page.get_by_role('link', name='Loan L4').click()
            page.get_by_role('button', name='Mark as returned').click()
            page.wait_for_url(f'{live_server.url}/ui/loans/L4/')

            assert page.get_by_text('Not yet returned').count() == 0
        finally:
            browser.close()
