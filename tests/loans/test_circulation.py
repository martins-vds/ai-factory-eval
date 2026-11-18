from datetime import timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan


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
    assert Loan.objects.get(pk='L2').returned_on == original_return_date
