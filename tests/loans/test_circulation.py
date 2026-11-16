from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_lending_creates_a_durable_fourteen_day_loan(client):
    today = timezone.localdate()

    response = client.post('/loans', {'member': 'dee', 'isbn': '123'})

    assert response.status_code == 201
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L4;dee;123;{today.isoformat()};{(today + timedelta(days=14)).isoformat()};\n'
    )
    assert client.get('/loans/L4').content == response.content
    assert Loan.objects.get(pk='L4').lent_on == today


@pytest.mark.django_db
def test_characterized_api_posts_work_without_browser_csrf_tokens():
    api_client = Client(enforce_csrf_checks=True)

    lending = api_client.post('/loans', {'member': 'dee', 'isbn': '123'})
    returning = api_client.post('/loans/L1/return')

    assert lending.status_code == 201
    assert returning.status_code == 200


@pytest.mark.parametrize(
    ('path', 'data'),
    [('/ui/loans/new/', {'member': 'dee', 'isbn': '123'}), ('/ui/loans/L1/return/', {})],
)
@pytest.mark.django_db
def test_browser_actions_require_csrf_tokens(path, data):
    browser_client = Client(enforce_csrf_checks=True)

    response = browser_client.post(path, data)

    assert response.status_code == 403


@pytest.mark.parametrize(
    ('member', 'isbn'),
    [('', '123'), ('  ', '123'), ('reader', ''), ('reader', '  ')],
)
@pytest.mark.django_db
def test_lending_rejects_blank_member_or_isbn(client, member, isbn):
    existing_loans = Loan.objects.count()

    response = client.post('/loans', {'member': member, 'isbn': isbn})

    assert response.status_code == 400
    assert response.content.decode() == 'member and isbn are required\n'
    assert Loan.objects.count() == existing_loans


@pytest.mark.django_db
def test_returning_a_loan_records_today_and_returns_its_formatted_record(client):
    today = timezone.localdate()

    response = client.post('/loans/L1/return')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == (
        f'L1;ana;9780134685991;2026-01-02;2026-01-16;{today.isoformat()}\n'
    )
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_repeating_a_return_is_rejected_without_changing_its_original_date(client):
    original_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/loans/L2/return')

    assert response.status_code == 409
    assert response.content.decode() == 'loan already returned\n'
    assert Loan.objects.get(pk='L2').returned_on == original_date


@pytest.mark.django_db
def test_returning_an_unknown_loan_keeps_the_characterized_not_found_response(client):
    response = client.post('/loans/unknown/return')

    assert response.status_code == 404
    assert response['Content-Type'] == 'text/plain'
    assert response.content.decode() == 'no such loan\n'


@pytest.mark.django_db
def test_loan_browser_offers_lending_and_first_return_actions(client):
    response = client.get('/ui/loans/')
    page = response.content.decode()

    assert response.status_code == 200
    assert 'Books in good company.' in page
    assert 'action="/ui/loans/new/"' in page
    assert 'action="/ui/loans/L1/return/"' in page
    assert 'hx-boost="true"' in page
    assert 'Return L1' in page


@pytest.mark.django_db
def test_browser_lending_shows_field_errors_for_blank_values(client):
    existing_loans = Loan.objects.count()

    response = client.post('/ui/loans/new/', {'member': '  ', 'isbn': ''})
    page = response.content.decode()

    assert response.status_code == 200
    assert 'Enter a member name; blank values are not accepted.' in page
    assert 'Enter an ISBN; blank values are not accepted.' in page
    assert 'aria-invalid="true"' in page
    assert Loan.objects.count() == existing_loans


@pytest.mark.django_db
def test_browser_lending_creates_a_loan_and_shows_feedback(client):
    response = client.post('/ui/loans/new/', {'member': ' reader ', 'isbn': '123'})
    page = response.content.decode()

    loan = Loan.objects.get(pk='L4')
    assert response.status_code == 200
    assert 'Loan L4 added to the collection.' in page
    assert loan.member == 'reader'
    assert loan.isbn == '123'


@pytest.mark.django_db
def test_browser_return_marks_loan_and_shows_status(client):
    today = timezone.localdate()

    response = client.post('/ui/loans/L1/return/')
    page = response.content.decode()

    assert response.status_code == 200
    assert 'L1 marked returned today.' in page
    assert f'Returned {today.strftime("%b")} {today.day}, {today.year}' in page
    assert Loan.objects.get(pk='L1').returned_on == today


@pytest.mark.django_db
def test_browser_repeated_return_is_rejected_and_preserves_original_date(client):
    original_date = Loan.objects.get(pk='L2').returned_on

    response = client.post('/ui/loans/L2/return/')

    assert response.status_code == 200
    assert (
        f'L2 was already returned on {original_date}; repeat return rejected '
        'and original date retained.'
    ) in response.content.decode()
    assert Loan.objects.get(pk='L2').returned_on == original_date
