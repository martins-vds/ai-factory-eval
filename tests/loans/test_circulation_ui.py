from datetime import timedelta

import pytest
from django.utils import timezone

from src.loans.models import Loan


def server_today():
    return timezone.localdate(timezone.now(), timezone.get_default_timezone())


@pytest.mark.django_db
def test_new_loan_page_is_linked_from_the_collection(client):
    collection = client.get('/ui/loans/')
    form = client.get('/ui/loans/new/')

    assert collection.status_code == 200
    assert b'/ui/loans/new/' in collection.content
    assert form.status_code == 200
    assert b'name="member"' in form.content
    assert b'name="isbn"' in form.content


@pytest.mark.django_db
def test_browser_lending_redirects_to_the_new_loan(client):
    response = client.post('/ui/loans/new/', {'member': 'reader', 'isbn': '123'})

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L4/'
    loan = Loan.objects.get(pk='L4')
    assert loan.member == 'reader'
    assert loan.isbn == '123'
    assert loan.due_on == server_today() + timedelta(days=14)


@pytest.mark.django_db
def test_browser_lending_renders_field_errors(client):
    response = client.post('/ui/loans/new/', {'member': ' \t ', 'isbn': ''})

    assert response.status_code == 400
    assert b'<!doctype html>' in response.content
    assert b'This field is required.' in response.content
    assert Loan.objects.count() == 3


@pytest.mark.django_db
def test_htmx_lending_renders_validation_errors(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': '', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 400
    assert b'id="loan-form"' in response.content
    assert b'This field is required.' in response.content


@pytest.mark.django_db
def test_htmx_lending_redirects_to_created_loan(client):
    response = client.post(
        '/ui/loans/new/',
        {'member': 'reader', 'isbn': '123'},
        HTTP_HX_REQUEST='true',
    )

    assert response.status_code == 204
    assert response['HX-Redirect'] == '/ui/loans/L4/'


@pytest.mark.django_db
def test_loan_detail_offers_htmx_return_and_updates_the_page(client):
    detail = client.get('/ui/loans/L1/')

    assert detail.status_code == 200
    assert b'hx-post="/ui/loans/L1/return/"' in detail.content

    response = client.post('/ui/loans/L1/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 200
    assert b'Returned' in response.content
    assert b'Nov' in response.content
    assert Loan.objects.get(pk='L1').returned_on == server_today()


@pytest.mark.django_db
def test_regular_return_redirects_to_updated_loan(client):
    response = client.post('/ui/loans/L1/return/')

    assert response.status_code == 302
    assert response['Location'] == '/ui/loans/L1/'
    assert Loan.objects.get(pk='L1').returned_on == server_today()


@pytest.mark.django_db
def test_regular_repeat_return_renders_the_loan_and_original_date(client):
    original_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/ui/loans/L2/return/')

    assert response.status_code == 409
    assert b'Loan record \xc2\xb7 L2' in response.content
    assert b'Jan 20, 2026' in response.content
    assert b'Loan already returned' in response.content
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_regular_unknown_return_returns_a_plain_text_not_found(client):
    response = client.post('/ui/loans/missing/return/')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content == b'no such loan\n'


@pytest.mark.django_db
def test_htmx_return_renders_a_repeat_error_and_keeps_the_date(client):
    original_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/ui/loans/L2/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 409
    assert b'already returned' in response.content
    assert b'Jan 20, 2026' in response.content
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_htmx_return_renders_an_unknown_loan_error(client):
    response = client.post('/ui/loans/missing/return/', HTTP_HX_REQUEST='true')

    assert response.status_code == 404
    assert b'no such loan' in response.content
