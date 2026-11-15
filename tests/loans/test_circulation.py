from datetime import timedelta

import pytest
from django.utils import timezone
from playwright.sync_api import expect, sync_playwright

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_the_characterized_record(client):
    lent_on = timezone.localdate()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{lent_on.isoformat()};{(lent_on + timedelta(days=14)).isoformat()};\n'
    )

    persisted = client.get('/loans/L4')
    assert persisted.status_code == 200
    assert persisted.content == response.content


@pytest.mark.django_db
def test_lending_preserves_field_content_and_escapes_export_delimiters(client):
    lent_on = timezone.localdate()
    member = ' Reader; Example\nSecond line '

    response = client.post('/loans', {'member': member, 'isbn': '978"xyz'})

    assert response.status_code == 201
    assert response.content.decode() == (
        f'L4;"{member}";"978""xyz";{lent_on.isoformat()};'
        f'{(lent_on + timedelta(days=14)).isoformat()};\n'
    )


@pytest.mark.django_db
def test_returning_a_loan_records_today_and_rejects_a_repeat(client):
    returned_on = timezone.localdate()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{returned_on.isoformat()}\n'
    )

    repeated = client.post('/loans/L2/return')
    assert repeated.status_code == 409
    assert repeated.content.decode() == 'loan already returned\n'
    assert client.get('/loans/L2').content.decode() == (
        'L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\n'
    )


@pytest.mark.django_db
def test_returning_unknown_loan_returns_the_characterized_not_found_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_return_endpoint_only_accepts_post(client):
    response = client.get('/loans/L1/return')

    assert response.status_code == 405
    assert client.get('/loans/L1').content.decode() == (
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    )


@pytest.mark.django_db
def test_loan_collection_only_accepts_get_and_post(client):
    response = client.put('/loans')

    assert response.status_code == 405


@pytest.mark.django_db
def test_lending_form_shows_field_errors_for_blank_values(client):
    page = client.get('/ui/loans/new/')

    assert page.status_code == 200
    response = client.post('/ui/loans/new/', {'member': 'reader', 'isbn': '   '})

    assert response.status_code == 400
    assert b'id_isbn' in response.content
    assert b'This field is required.' in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fields',
    [
        {},
        {'member': '', 'isbn': '123'},
        {'member': '   ', 'isbn': '123'},
        {'member': 'reader', 'isbn': '   '},
    ],
)
def test_api_lending_rejects_missing_or_blank_fields(client, fields):
    response = client.post('/loans', fields)

    assert response.status_code == 400
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == 3


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_reader_can_lend_and_return_a_book_in_the_browser(live_server):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f'{live_server.url}/ui/loans/')
            page.get_by_role('link', name='Lend a book').click()
            page.get_by_label('Member').fill('reader')
            page.get_by_label('ISBN').fill('978123')
            page.get_by_role('button', name='Lend book').click()

            loan = page.locator('#loan-L4')
            expect(loan.get_by_text('reader · ISBN 978123')).to_be_visible()
            loan.get_by_role('button', name='Return book').click()
            expect(loan.get_by_text('Returned')).to_be_visible()
            expect(loan.get_by_role('button', name='Return book')).to_have_count(0)
        finally:
            browser.close()


@pytest.mark.django_db
def test_browser_workflow_leaves_seed_records_available(client):
    response = client.get('/loans')

    assert response.status_code == 200
    assert response.content.decode().startswith(
        'L1;ana;9780134685991;2026-01-02;2026-01-16;\n'
    )
