from datetime import timedelta

import pytest
from django.utils import timezone
from django.utils.dateparse import parse_date
from playwright.sync_api import sync_playwright

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_a_loan_with_a_fourteen_day_due_date(client):
    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    lent_on = timezone.localdate()
    due_on = lent_on + timedelta(days=14)

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{due_on.isoformat()};\n'
    )


@pytest.mark.django_db
def test_returning_a_loan_records_the_server_date(client):
    response = client.post('/loans/L1/return')

    returned_on = timezone.localdate()
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )


@pytest.mark.django_db
def test_repeated_api_return_is_rejected_without_changing_the_original_date(client):
    original_date = parse_date('2026-01-20')

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response.content.decode() == 'already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_lending_api_rejects_missing_and_blank_required_fields(client):
    for data, field in (
        ({'isbn': '123'}, 'member'),
        ({'member': 'reader'}, 'isbn'),
        ({'member': '  ', 'isbn': '123'}, 'member'),
        ({'member': 'reader', 'isbn': '  '}, 'isbn'),
    ):
        response = client.post('/loans', data)

        assert response.status_code == 400
        assert field in response.content.decode()


@pytest.mark.django_db
def test_lend_form_shows_field_errors_for_blank_values(client):
    response = client.post('/ui/loans/', {'member': '  ', 'isbn': ''})

    assert response.status_code == 400
    assert b'Enter a member name; blank values are not accepted.' in response.content
    assert b'Enter an ISBN; blank values are not accepted.' in response.content


@pytest.mark.django_db
def test_lend_form_page_and_successful_browser_lending(client):
    form_page = client.get('/ui/loans/new/')

    assert form_page.status_code == 200
    assert b'name="member"' in form_page.content
    assert b'name="isbn"' in form_page.content

    response = client.post('/ui/loans/', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/'
    collection = client.get(response['Location'])
    assert b'Loan L4' in collection.content
    assert b'reader' in collection.content


@pytest.mark.django_db
def test_lend_form_page_rejects_post_requests(client):
    response = client.post('/ui/loans/new/')

    assert response.status_code == 405


@pytest.mark.django_db
def test_browser_return_updates_a_loan_row_and_rejects_repeated_return(client):
    first_return = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert first_return.status_code == 200
    assert b'Returned' in first_return.content
    assert b'Mark returned' not in first_return.content

    repeated_return = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert repeated_return.status_code == 200
    assert b'already returned on ' in repeated_return.content
    assert b'Mark returned' not in repeated_return.content
    assert str(Loan.objects.get(pk='L1').returned_on).encode() in repeated_return.content


@pytest.mark.django_db
def test_return_api_preserves_the_characterized_unknown_loan_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_browser_can_lend_a_book_and_return_it_with_htmx(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/loans/')
            page.get_by_role('link', name='Lend a book').click()
            page.get_by_label('Member').fill('browser reader')
            page.get_by_label('ISBN').fill('123')
            page.get_by_role('button', name='Add loan').click()
            page.get_by_role('heading', name='Loan L4').wait_for()

            first_loan = page.locator('#loan-L1')
            first_loan.get_by_role('button', name='Mark returned').click()
            first_loan.get_by_text('Returned', exact=False).wait_for()

            assert page.url.endswith('/ui/loans/')
        finally:
            browser.close()
